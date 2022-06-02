from os import mkdir, system
from typing import Callable, Iterable
import os.path
import requests as req

ACL_HEADER = '''[bypass_all]
[proxy_list]
'''
DATA_URL = 'https://reestr.rublacklist.net/api/v2/domains/json'

OUT_DIR = 'public'
ORIGINAL_FILE = 'domains.txt'
DOMAINS_FILE = 'domains-new.txt'
FILTERED_FILE = 'filtered.txt'

get_data = lambda: req.get(DATA_URL).json()
# def get_data():
# 	with open('domains.json') as f:
# 		import json
# 		return json.load(f)

def write_list(filename: str, data: Iterable[str], *, acl = False):
	header = ACL_HEADER if acl else ''
	with open(filename, 'w') as file:
		file.write(header + '\n'.join(data) + '\n')

def read_list(filename: str):
	with open(filename) as file:
		data = file.read()
	return data.strip().split('\n')

# https://stackoverflow.com/a/71922468
to_puny = lambda s: s.encode('idna').decode()
def from_puny(s: str):
	try:
		return s.encode().decode('idna')
	except UnicodeDecodeError:
		return s
	except UnicodeError as e:
		print(f'[decode] {e}:', s)
		return s

def convert_domains(domains: Iterable[str]) -> list[str]:
	convert: Callable[[str], str] = lambda d: r'(?:^|\.)' + d.replace('.', r'\.') + '$'

	uniq_domains = set(to_puny(d) for d in domains)
	return list(map(convert, domains2tld(uniq_domains)))

def domains2tld(domains: Iterable[str]) -> list[str]:
	""" ['ex.com', 'm.ex.com'] -> ['ex.com'] """
	tlds = set()
	for d in domains:
		parts = d.split('.')

		# add IP
		if parts[-1].isdigit():
			tlds.add(d)
			continue

		# add TLD
		tlds.add('.'.join(parts[-2:]))

	return list(tlds)

def main():
	print('[main] fetch data')
	domains = get_data()
	write_list(ORIGINAL_FILE, (from_puny(d) for d in domains))

	system('./filter.sh')

	domains = read_list(DOMAINS_FILE)
	filtered_domains = read_list(FILTERED_FILE)

	if not os.path.exists(OUT_DIR):
		mkdir(OUT_DIR)

	print('[main] convert main domains')
	domains = convert_domains(domains)
	print('[main] convert filtered domains')
	filtered_domains = convert_domains(filtered_domains)
	# remove duplicates
	filtered_domains = set(filtered_domains) - set(domains)

	write_list(os.path.join(OUT_DIR, 'ru.acl'), domains, acl=True)
	write_list(os.path.join(OUT_DIR, 'ru-filtered.acl'), filtered_domains, acl=True)

if __name__ == '__main__':
	main()
