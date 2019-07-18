from django.urls import reverse
from elecciones.tests.factories import (
    VotoMesaReportadoFactory,
    CategoriaFactory,
    MesaFactory,
    OpcionFactory,
    CircuitoFactory,
    CategoriaOpcionFactory,
    CargaFactory,
    IdentificacionFactory,
)
from elecciones.tests.test_resultados import fiscal_client, setup_groups # noqa
from elecciones.models import Mesa, VotoMesaReportado, Carga, MesaCategoria
from http import HTTPStatus
from elecciones.tests.test_resultados import fiscal_client          # noqa
from adjuntos.consolidacion import *
from elecciones.tests.test_models import consumir_novedades_y_actualizar_objetos


def test_elegir_acta_sin_mesas(fiscal_client):
    response = fiscal_client.get(reverse('siguiente-accion'))
    assert 'No hay actas para cargar por el momento' in response.content.decode('utf8')


def test_elegir_acta_mesas_redirige(db, fiscal_client):
    assert Mesa.objects.count() == 0
    assert VotoMesaReportado.objects.count() == 0
    c = CircuitoFactory(id = 100001)
    e1 = CategoriaFactory()
    e2 = CategoriaFactory()

    m1 = IdentificacionFactory(
        mesa__categorias=[e1],
        mesa__lugar_votacion__circuito=c,
        status='identificada',
        source=Identificacion.SOURCES.csv,
    ).mesa
    e2 = CategoriaFactory()
    m2 = IdentificacionFactory(
        mesa__categorias=[e1, e2],
        mesa__lugar_votacion__circuito=c,
        status='identificada',
        source=Identificacion.SOURCES.csv,
    ).mesa
    
    consumir_novedades_identificacion()

    response = fiscal_client.get(reverse('siguiente-accion'))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('mesa-cargar-resultados', args=[e1.id, m1.numero])

    # como m1 queda en periodo de "taken" (aunque no se haya ocupado aún)
    # se pasa a la siguiente mesa
    response = fiscal_client.get(reverse('siguiente-accion'))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('mesa-cargar-resultados', args=[e1.id, m2.numero])

    # se carga esa categoría.
    VotoMesaReportadoFactory(
        carga__mesa_categoria__mesa=m2,
        carga__mesa_categoria__categoria=e1,
        opcion=e1.opciones.first(),
        votos=1
    )


    # FIX ME . El periodo de taken deberia ser *por categoria*.
    # en este escenario donde esta lockeado la mesa para la categoria 1, pero no se está
    # cargando la mesa 2, un dataentry queda idle
    response = fiscal_client.get(reverse('siguiente-accion'))
    assert response.status_code == 200   # no hay actas

    m2.taken = None
    m2.save()
    response = fiscal_client.get(reverse('siguiente-accion'))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse(
        'mesa-cargar-resultados', args=[e2.id, m2.numero]
    )



def test_elegir_acta_prioriza_por_tamaño_circuito(db, fiscal_client):
    e1 = CategoriaFactory()

    m1 = IdentificacionFactory(
        mesa__categorias=[e1],
        status='identificada',
        source=Identificacion.SOURCES.csv,
    ).mesa
    m2 = IdentificacionFactory(
        mesa__categorias=[e1],
        status='identificada',
        source=Identificacion.SOURCES.csv,
    ).mesa
    m3 = IdentificacionFactory(
        mesa__categorias=[e1],
        status='identificada',
        source=Identificacion.SOURCES.csv,
    ).mesa
    consumir_novedades_identificacion()
    # creo otras mesas asociadas a los circuitos
    c1 = m1.lugar_votacion.circuito
    c2 = m2.lugar_votacion.circuito
    c3 = m3.lugar_votacion.circuito

    MesaFactory.create_batch(
        3,
        categorias=[e1],
        lugar_votacion__circuito=c1
    )
    MesaFactory.create_batch(
        10,
        categorias=[e1],
        lugar_votacion__circuito=c2
    )
    MesaFactory.create_batch(
        5,
        categorias=[e1],
        lugar_votacion__circuito=c3
    )
    assert c1.electores == 400
    assert c2.electores == 1100
    assert c3.electores == 600

    response = fiscal_client.get(reverse('siguiente-accion'))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('mesa-cargar-resultados', args=[e1.id, m2.numero])
    response = fiscal_client.get(reverse('siguiente-accion'))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('mesa-cargar-resultados', args=[e1.id, m3.numero])
    response = fiscal_client.get(reverse('siguiente-accion'))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('mesa-cargar-resultados', args=[e1.id, m1.numero])


def test_carga_mesa_redirige_a_siguiente(db, fiscal_client):
    o = OpcionFactory(es_contable=True)
    o2 = OpcionFactory(es_contable=False)
    e1 = CategoriaFactory(opciones=[o, o2])
    e2 = CategoriaFactory(opciones=[o])
    m1 = IdentificacionFactory(
        mesa__categorias=[e1, e2],
        status='identificada',
        source=Identificacion.SOURCES.csv,
    ).mesa
    consumir_novedades_identificacion()
    response = fiscal_client.get(reverse('siguiente-accion'))
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('mesa-cargar-resultados', args=[e1.id, m1.numero])
    # formset para categoria e1 arranca en blanco
    url = response.url
    response = fiscal_client.get(response.url)
    formset = response.context['formset']
    assert len(formset) == 2
    assert formset[0].initial == {'opcion': o}
    assert formset[1].initial == {'opcion': o2}


    tupla_opciones_electores = [(o.id, m1.electores // 2), (o2.id, m1.electores // 2)]
    request_data = _construir_request_data_para_carga_de_resultados(tupla_opciones_electores)
    # response = fiscal_client.get(url)
    response = fiscal_client.post(url, request_data)
    carga = Carga.objects.get()  # sólo hay una carga
    assert carga.tipo == Carga.TIPOS.total
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('siguiente-accion')
    # en rigor, aca habria que probar que
    # aparece la siguiente categoria de la misma acta
    # igualmente esta logica debería cambiar en breve
    # por la misma razon, el resto del test no tiene sentido
    # Carlos Lombardi, 2019.7.9

    # el form de la nueva categoria e2 está en blanco
    # url = response.url
    # response = fiscal_client.get(response.url)
    # formset = response.context['formset']
    # assert len(formset) == 1
    # assert formset[0].initial == {'opcion': o}

    # # si completamos y es valido, no quedan
    # # categorias por cargar y pide otra acta
    # response = fiscal_client.post(url, {
    #     'form-0-opcion': str(o.id),
    #     'form-0-votos': str(m1.electores),
    #     'form-TOTAL_FORMS': '1',
    #     'form-INITIAL_FORMS': '0',
    #     'form-MIN_NUM_FORMS': '1',
    #     'form-MAX_NUM_FORMS': '1000',
    # })
    # assert response.status_code == HTTPStatus.FOUND
    # assert response.url == reverse('post-cargar-resultados', args=[m1.numero, e2.nombre])



def _construir_request_data_para_carga_de_resultados(tuplas_opcion_electores):
    """
    Métodito que sirve para ahorrarnos el tema este crear el diccionario para la data del request
    al momento de cargar resultados.

    Se puede hacer más parametrizable.

    Las tuplas opcion_electores tienen que tener (opcion_id, cant_electores)
    """

    request_data = {}
    index = 0
    for tupla in tuplas_opcion_electores:
        key = f'form-{index}-opcion'
        request_data[key] = str(tupla[0])
        key = f'form-{index}-votos'
        request_data[key] = str(tupla[1])
        index = index + 1
    request_data['form-TOTAL_FORMS'] = str(len(tuplas_opcion_electores))
    request_data['form-INITIAL_FORMS'] = '0'
    request_data['form-MIN_NUM_FORMS'] = '2'
    request_data['form-MAX_NUM_FORMS'] = '1000'
    return request_data

def test_formset_en_carga_parcial(db, fiscal_client):
    c = CategoriaFactory()
    o = CategoriaOpcionFactory(categoria=c, prioritaria=True).opcion
    o2 = CategoriaOpcionFactory(categoria=c, prioritaria=False).opcion
    m = MesaFactory(categorias=[c])
    parciales = reverse(
        'mesa-cargar-resultados-parciales', args=[c.id, m.numero]
    )
    response = fiscal_client.get(parciales)
    assert len(response.context['formset']) == 1
    response.context['formset'][0].fields['opcion'].choices == [
        (o.id, str(o))
    ]


def test_formset_en_carga_total(db, fiscal_client):
    c = CategoriaFactory(id=100, opciones=[])
    o = CategoriaOpcionFactory(categoria=c, opcion__orden=3, prioritaria=True).opcion
    o2 = CategoriaOpcionFactory(categoria=c, opcion__orden=1, prioritaria=False).opcion
    m = MesaFactory(categorias=[c])
    totales = reverse(
        'mesa-cargar-resultados', args=[c.id, m.numero]
    )
    response = fiscal_client.get(totales)
    assert len(response.context['formset']) == 2
    response.context['formset'][0].fields['opcion'].choices == [
        (o2.id, str(o2)),
        (o.id, str(o))
    ]


def test_detalle_mesa_categoria(db, fiscal_client):
    opcs = OpcionFactory.create_batch(3, es_contable=True)
    e1 = CategoriaFactory(opciones=opcs)
    e2 = CategoriaFactory(opciones=opcs)
    mesa = MesaFactory(categorias=[e1, e2])
    c1 = CargaFactory(
            mesa_categoria__mesa=mesa,
            mesa_categoria__categoria=e1,
            tipo=Carga.TIPOS.parcial,
            origen=Carga.SOURCES.csv
    )
    mc = c1.mesa_categoria
    votos1 = VotoMesaReportadoFactory(
        opcion=opcs[0],
        votos=1,
        carga=c1,
    )
    votos2 = VotoMesaReportadoFactory(
        opcion=opcs[1],
        votos=2,
        carga=c1,
    )
    votos3 = VotoMesaReportadoFactory(
        opcion=opcs[2],
        votos=1,
        carga=c1,
    )

    # a otra carga
    vm = VotoMesaReportadoFactory(
        opcion=opcs[2],
        votos=1
    )
    c1.actualizar_firma()
    consumir_novedades_y_actualizar_objetos([mc])
    assert mc.carga_testigo == c1
    url = reverse('detalle-mesa-categoria', args=[e1.id, mesa.numero])
    response = fiscal_client.get(url)

    assert list(response.context['reportados']) == [votos1, votos2, votos3]



def test_cargar_resultados_mesa_desde_ub_con_id_de_mesa(fiscal_client):
    """
    Es un test desaconsejadamente largo, pero me sirvió para entender el escenario.
    Se hace un recorrido por la carga de dos categorías desde una UB.

    Cuando se llama a procesar-acta-mesa, cuando va por GET, es para cargar el template carga-ub.html.
    Cuando se le pega con POST, va a cargar un resultado.

    Cuando ya no tiene más categorías para cargar, te devuelve a agregar-adjunto-ub

    """
    circuito = CircuitoFactory()
    categoria_1 = CategoriaFactory()
    categoria_2 = CategoriaFactory()
    opcion1 = CategoriaOpcionFactory(categoria=categoria_1, prioritaria=True).opcion
    opcion2 = CategoriaOpcionFactory(categoria=categoria_1, prioritaria=False).opcion

    opcion3 = CategoriaOpcionFactory(categoria=categoria_2, prioritaria=True).opcion
    opcion4 = CategoriaOpcionFactory(categoria=categoria_2, prioritaria=False).opcion

    nombre_categoria = "Un nombre especifico"
    categoria_1.nombre = nombre_categoria
    categoria_1.save(update_fields=['nombre'])

    mesa1 = IdentificacionFactory(
        mesa__categorias=[categoria_1, categoria_2],
        mesa__lugar_votacion__circuito=circuito,
        status='identificada'
    ).mesa

    response = fiscal_client.get(reverse('procesar-acta-mesa', kwargs={'mesa_id': mesa1.id}))
    
    assert response.status_code == HTTPStatus.OK
    #nos aseguramos que haya cargado el template específico para UB
    assert "/clasificar-actas/ub/agregar" in str(response.content)  
    #como es por id el order by del método que devuelve siguiente categoria, debería ser categoria_1
    assert nombre_categoria in str(response.content)
    
    tupla_opciones_electores = [(opcion1.id, mesa1.electores // 2), (opcion2.id, mesa1.electores // 2)]
    request_data = _construir_request_data_para_carga_de_resultados(tupla_opciones_electores)
    
    url_carga_resultados = response.context['request'].get_full_path()

    response = fiscal_client.post(url_carga_resultados, request_data)
    
    #tiene otra categoría, por lo que debería cargar y redirigirnos nuevamente a procesar-acta-mesa    
    carga = Carga.objects.get() 

    assert carga.tipo == Carga.TIPOS.total
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('procesar-acta-mesa', kwargs={'mesa_id': mesa1.id})

    tupla_opciones_electores = [(opcion3.id, mesa1.electores // 2), (opcion4.id, mesa1.electores // 2)]

    response = fiscal_client.post(url_carga_resultados, request_data)

    consumir_novedades_y_actualizar_objetos([carga.mesa_categoria])

    #ya no tiene más categorías, debe dirigirnos a subir-adjunto
    cargas = Carga.objects.all()
    assert 2 == len(cargas)
    assert carga.tipo == Carga.TIPOS.total
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == reverse('procesar-acta-mesa', kwargs={'mesa_id': mesa1.id})

    response = fiscal_client.post(url_carga_resultados)

    #la mesa no tiene más categorías, nos devuelve a la pantalla de carga de adjuntos
    assert response.url == reverse('agregar-adjuntos-ub')

    

def test_elegir_acta_mesas_con_id_inexistente_de_mesa_desde_ub(fiscal_client):
    mesa_id_inexistente = 673162312
    response = fiscal_client.get(reverse('procesar-acta-mesa', kwargs={'mesa_id': mesa_id_inexistente}))
    
    assert response.status_code == HTTPStatus.NOT_FOUND