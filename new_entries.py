import time
import osmium.osm

from uuid import uuid4
from datetime import datetime, timezone

from .normalization import AddressNormalization


class NewEntryXMLActions:

    @classmethod
    async def create_new_entry(cls, data, filename=None):
        filename = f'{uuid4()}.osm.xml' if filename == None else filename
        with osmium.SimpleWriter(filename) as writer:
            entry_id = round(time.time() * 1000)
            if isinstance(data, list):
                for entry in data:
                    newEntry = await cls.populate_entry(entry, entry_id)
                    entry_id+=1
                    writer.add_node(newEntry)
                    writer.add_node(cls.create_place_entry(newEntry, entry_id))
                    entry_id+=1
            else:
                newEntry = await cls.populate_entry(data, entry_id)
                writer.add_node(newEntry)
                writer.add_node(cls.create_place_entry(newEntry, entry_id))        
        return {
            "status": 200,
            "filename": filename
        }


    @classmethod
    async def populate_entry(cls, data, entry_id):
        data = AddressNormalization.parsed_street_to_model(data, AddressNormalization.parse_address(data.create_full_str()))
        newEntry = osmium.osm.mutable.Node(
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            id = entry_id,
            user = "osm_imports",
            version = 1,
            tags = cls.set_tags(data),
            location = cls.set_location(data),
            visible = True
        )
        return newEntry


    @staticmethod
    def set_tags(data):
        tagList = []
        for key, value in data.__dict__.items():
            if key in ['street', 'housenumber', 'unit', 'city', 'state', 'postcode', 'country']:
                tagList.append(osmium.osm.Tag(f"addr:{key}", str(value)))
        return tagList
    

    @staticmethod
    def set_location(data):
        datakeys = data.__dict__.keys()
        if 'lat' in datakeys and 'lon' in datakeys:
            return (float(data.lon), float(data.lat))
        if data.latitude and data.longitude:
            return (float(data.longitude), float(data.latitude))
        return (0, 0)
    
    
    def create_place_entry(entry, entry_id):
        entry.id = entry_id
        for i in entry.tags:
            if 'addr:street' in i: 
                entry.tags[entry.tags.index(i)] = osmium.osm.Tag("addr:place", i[1])
        return entry
