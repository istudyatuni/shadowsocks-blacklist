from os import mkdir, system
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

def write_list(filename: str, data: list, *, acl = False):
	header = ACL_HEADER if acl else ''
	with open(filename, 'w') as file:
		file.write(header + '\n'.join(data) + '\n')

def read_list(filename: str):
	with open(filename) as file:
		data = file.read()
	return data.strip().split('\n')

# https://stackoverflow.com/a/71922468
to_puny = lambda s: s.encode('idna').decode()

def convert_domains(domains: list[str]) -> list[str]:
	uniq_domains = set(to_puny(d) for d in domains)

	converted: list[str] = []
	for d in uniq_domains:
		if d.startswith('*.'):
			d = d.lstrip('*.')
		d = d.replace('.', r'\.')
		converted.append(r'(?:^|\.)' + d + '$')

	return converted

def main():
	domains = get_data()
	write_list(ORIGINAL_FILE, domains)

	system('./filter.sh')

	domains = read_list(DOMAINS_FILE)
	filtered_domains = read_list(FILTERED_FILE)

	mkdir(OUT_DIR)
	write_list(os.path.join(OUT_DIR, 'ru.acl'), convert_domains(domains), acl=True)
	write_list(os.path.join(OUT_DIR, 'ru-filtered.acl'), convert_domains(filtered_domains), acl=True)

if __name__ == '__main__':
	main()
