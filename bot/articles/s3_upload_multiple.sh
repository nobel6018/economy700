#!/usr/bin/env bash

start_file=$1
end_file=$2

for (( i=start_file; i<=end_file; i++ ))
do
  file_name=$i.json

  aws s3 cp json/$file_name s3://economy700/$file_name --content-type "application/json; charset=utf-8" --profile=googit

  for arg in "$@"
  do
    if [ "$arg" == "--invalidate" ] || [ "$arg" == "--invalidate=true" ] || [ "$arg" == "--invalidate true" ]; then
      # invalidate cloudfront cache
      aws cloudfront create-invalidation --distribution-id E27JTE8ROOFOX0 --paths "/$file_name" --profile=googit
      echo "Cloudfront cache invalidated for $file_name"
    fi
  done
done
