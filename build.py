"""Validate editable lists and build native sing-box source rule sets."""
import ipaddress
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent


def entries(filename):
    result = set()
    for number, line in enumerate((ROOT / filename).read_text(encoding='utf-8').splitlines(), 1):
        value = line.split('#', 1)[0].split('//', 1)[0].strip().lower()
        if not value:
            continue
        if filename == 'domains.txt':
            if not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}', value) or len(value) > 253:
                raise ValueError(f'{filename}:{number}: expected a domain without protocol or path: {value!r}')
        else:
            network = ipaddress.ip_network(value, strict=True)
            if network.version != 4 or network.prefixlen == 0:
                raise ValueError(f'{filename}:{number}: expected an IPv4 subnet other than the default route')
            value = str(network)
        result.add(value)
    if not result:
        raise ValueError(f'{filename}: list must not be empty')
    return sorted(result)


for stem, key in [('domains', 'domain_suffix'), ('subnets', 'ip_cidr')]:
    values = entries(stem + '.txt')
    data = {'version': 3, 'rules': [{key: values}]}
    (ROOT / (stem + '.json')).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'{stem}: {len(values)} entries')
