'''
Created on 24 août 2017

@author: julien
'''
import json

from zigraph.discosearch import DiscoSearch

INFOS = DiscoSearch().search('Charles Mingus', 'Goodbye Pork Pie Hat')
print(json.dumps(INFOS, sort_keys=True, indent=4))
