#!/usr/bin/env bash
# Downloads the Wikimedia Commons photos used on the site into images/<destination>/
# so pages load from this repo instead of hotlinking commons.wikimedia.org on every
# request. Run this from the repo root on a machine with normal internet access:
#
#   bash scripts/fetch-images.sh
#
# Then commit the images/ folder and push.
set -euo pipefail

UA="Mozilla/5.0 (compatible; HoneymoonPlanningSite/1.0; personal-use)"
WIDTH=1600

mkdir -p images/italy

declare -A ITALY_IMAGES=(
  ["rome-skyline.jpg"]="Rome_skyline_panorama.jpg"
  ["positano-amalfi-coast.jpg"]="Positano-Amalfi_Coast-Italy.jpg"
  ["colosseum.jpg"]="Colosseum,_Rome.JPG"
  ["st-peters-basilica.jpg"]="Saint_Peter's_Basilica_facade,_Rome,_Italy.jpg"
  ["fornillo-beach.jpg"]="Positano_-_Fornillo_Beach.jpg"
  ["capri-faraglioni.jpg"]="CapriFaraglioni.JPG"
  ["path-of-the-gods.jpg"]="Il_Sentiero_degli_dei.jpg"
  ["villa-rufolo-ravello.jpg"]="Ravello_Villa_Rufolo.JPG"
  ["trastevere-piazza.jpg"]="Trastevere_-_piazza_san_Cosimato_00725-8.JPG"
  ["positano-panoramio-1.jpg"]="84017_Positano,_Province_of_Salerno,_Italy_-_panoramio.jpg"
  ["positano-panoramio-2.jpg"]="84017_Positano,_Province_of_Salerno,_Italy_-_panoramio_(1).jpg"
  ["costa-di-amalfi.jpg"]="Costa_di_Amalfi_-_Italia.jpg"
  ["positano-ii.jpg"]="Positano_II.jpg"
  ["positano-07.jpg"]="Positano_07.jpg"
  ["positano-01.jpg"]="Positano_-_01.jpg"
)

fail=0
for local_name in "${!ITALY_IMAGES[@]}"; do
  commons_name="${ITALY_IMAGES[$local_name]}"
  url="https://commons.wikimedia.org/wiki/Special:FilePath/${commons_name}?width=${WIDTH}"
  dest="images/italy/${local_name}"
  echo "Fetching ${local_name} ..."
  if ! curl -fsSL -A "$UA" -o "$dest" "$url"; then
    echo "  FAILED: $url" >&2
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo "One or more downloads failed — check the URLs/filenames above." >&2
  exit 1
fi

echo "Done. $(ls images/italy | wc -l) files in images/italy/"
