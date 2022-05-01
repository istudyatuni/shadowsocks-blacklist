#!/usr/bin/env bash

set -euo pipefail

filter=filter.txt
original=domains.txt
domains=domains-new.txt
filtered=filtered.txt

cp $original $domains
if [[ -f $filtered ]]; then
	rm $filtered
fi

while read str; do
	grep "$str" $domains >> $filtered

	grep -v "$str" $domains > .$domains
	mv .$domains $domains
done < $filter
