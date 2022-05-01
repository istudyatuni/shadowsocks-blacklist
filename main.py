import requests as req

ACL_HEADER = '''[bypass_all]
[proxy_list]
'''
DATA_URL = 'https://reestr.rublacklist.net/api/v2/domains/json'

def get_data():
	r = req.get(DATA_URL)
	return r.json()

# https://stackoverflow.com/a/71922468
puny_encode = lambda s: s.encode('idna').decode()

def main():
	domains = get_data()

	uniq_domains: set[str] = set()
	for d in domains:
		uniq_domains.add(puny_encode(d))

	converted_domains: list[str] = []
	for d in uniq_domains:
		if d.startswith('*.'):
			d1 = d.lstrip('*.')
		else:
			d1 = d
		d1 = d1.replace('.', r'\.')
		converted_domains.append(r'(?:^|\.)' + d1 + '$')

	with open('ru.acl', 'w') as file:
		file.write(ACL_HEADER + '\n'.join(converted_domains) + '\n')

if __name__ == '__main__':
	main()
