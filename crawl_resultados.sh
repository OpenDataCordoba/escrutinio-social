#!/bin/sh

dir_resultado=crawl-resultados

# Nos logueamos.
BASE_URI=localhost:8000
LOGIN_URL=http://${BASE_URI}/login/
USER='admin'
PASS='admin'
COOKIES=/tmp/cookies.txt
WGET_BIN="wget --load-cookies=$COOKIES --save-cookies=$COOKIES --referer=$LOGIN_URL"

echo "Django Auth: get csrftoken ..."
rm $COOKIES
$WGET_BIN --directory-prefix=/tmp $LOGIN_URL > /dev/null
DJANGO_TOKEN="csrfmiddlewaretoken=$(grep csrftoken $COOKIES | sed 's/^.*csrftoken\s*//')"

echo "Logueándose..."
$WGET_BIN \
	--directory-prefix=/tmp \
    --post-data="$DJANGO_TOKEN&username=$USER&password=$PASS" \
    $LOGIN_URL
DJANGO_TOKEN="csrfmiddlewaretoken=$(grep csrftoken $COOKIES | sed 's/^.*csrftoken\s*//')"

# Bajamos el sitio.
$WGET_BIN --page-requisites --recursive --level=100 --convert-links --html-extension --restrict-file-names=windows --no-parent --no-host-directories --directory-prefix=${dir_resultado} --span-hosts ${BASE_URI}/elecciones/resultados/1


echo "Reemplazando..."

# Reemplazamos referencias a localhost y sacamos el login y el logout.
find ${dir_resultado} -type f -name "*.html*" -exec sed -i -e 's/http:\/\/localhost:8000//g' -e '/href="\/login\/"/d' -e '/href="\/logout\/"/d' {} +

# Sacamos el desplegable de tipo de sumarización.
find ${dir_resultado} -type f -name "*.html*" -exec sed -i "s/id='tipodesumarizacion'/id='tipodesumarizacion' style='display:none'/g" {} +