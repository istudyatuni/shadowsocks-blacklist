#!/usr/bin/env bash

set -euo pipefail

filter='filter.txt'
original='domains.txt'
domains='domains-new.txt'
filtered='filtered.txt'

cp $original $domains
if [[ -f $filtered ]]; then
	rm $filtered
fi

echo [filter] start

while read str; do
	# grep will return code "1" if not found matches
	to_filter=$(grep "$str" $domains || :)
	if [[ -z "$to_filter" ]]; then
		continue
	fi
	echo "[filter] $str $(echo "$to_filter" | wc -l)"

	echo "$to_filter" >> $filtered

	grep -v "$str" $domains > .$domains
	mv .$domains $domains
done < $filter

echo [filter] done
