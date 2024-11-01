import re
from usaddress import tag
from string import punctuation
from rapidfuzz import fuzz, process

class AddressNormalization:

    STATE_ABV_TO_FULL = {
        "AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona", "CA": "California", "CO": "Colorado",
        "CT": "Connecticut", "DC": "District of Columbia", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
        "HI": "Hawaii", "IA": "Iowa", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "MA": "Massachusetts", "MD": "Maryland", "ME": "Maine", "MI": "Michigan",
        "MN": "Minnesota", "MO": "Missouri", "MS": "Mississippi", "MT": "Montana", "NC": "North Carolina",
        "ND": "North Dakota", "NE": "Nebraska", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
        "NV": "Nevada", "NY": "New York", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
        "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
        "UT": "Utah", "VA": "Virginia", "VT": "Vermont", "WA": "Washington", "WI": "Wisconsin", "WV": "West Virginia",
        "WY": "Wyoming", "AS": "American Samoa", "FM": "Federated States of Micronesia", "GU": "Guam",
        "MH": "Marshall Islands", "MP": "Northern Mariana Islands", "PW": "Palau", "PR": "Puerto Rico"}
    
    STATE_FULL_TO_ABV = {v: k for k, v in STATE_ABV_TO_FULL.items()}

    STATE_TO_CODE = {
        'AK': 0, 'AL': 1, 'AR': 2, 'AZ': 3, 'CA': 4, 'CO': 5, 'CT': 6,
        'DC': 7, 'DE': 8, 'FL': 9, 'GA': 10, 'HI': 11, 'IA': 12, 'ID': 13,
        'IL': 14, 'IN': 15, 'KS': 16, 'KY': 17, 'LA': 18, 'MA': 19, 'MD': 20,
        'ME': 21, 'MI': 22, 'MN': 23, 'MO': 24, 'MS': 25, 'MT': 26, 'NC': 27,
        'ND': 28, 'NE': 29, 'NH': 30, 'NJ': 31, 'NM': 32, 'NV': 33, 'NY': 34,
        'OH': 35, 'OK': 36, 'OR': 37, 'PA': 38, 'RI': 39, 'SC': 40, 'SD': 41,
        'TN': 42, 'TX': 43, 'UT': 44, 'VA': 45, 'VT': 46, 'WA': 47, 'WI': 48,
        'WV': 49, 'WY': 50, 'AS': 51, 'FM': 52, 'GU': 53, 'MH': 54, 'MP': 55,
        'PW': 56, 'PR': 57, 'VI': 58, 'AE': 59, 'AP': 60, 'AA': 61
    }

    CODE_TO_STATE = {v: k for k, v in STATE_TO_CODE.items()}

    @classmethod
    def full_state_to_code(cls, state):
        if state is None:
            return None
        state = cls.STATE_FULL_TO_ABV.get(state, state)
        return cls.STATE_TO_CODE.get(state, state)
    
    US_STREET_NAMES = {
        "alley": {"allee", "ally", "alley", "aly"},
        "annex": {"anex", "annex", "annx", "anx"},
        "arcade": {"arc", "arcade"},
        "avenue": {"av", "ave", "aven", "avenu", "avenue", "avn", "avnue"},
        "bayou": {"bayoo", "bayou", "byu"},
        "beach": {"bch", "beach"},
        "bend": {"bend", "bnd"},
        "bluff": {"blf", "bluf", "bluff"},
        "bluffs": {"blfs", "bluffs"},
        "bottom": {"bot", "bottm", "bottom", "btm"},
        "boulevard": {"bl", "blvd", "boul, boulv", "boulevard"},
        "branch": {"br", "branch", "brnch"},
        "bridge": {"brdge", "brg", "bridge"},
        "brook": {"brk", "brook"},
        "brooks": {"brks", "brooks"},
        "burg": {"bg", "burg"},
        "burgs": {"bgs", "burgs"},
        "bypass": {"byp", "bypa", "bypas", "bypass", "byps"},
        "camp": {"camp", "cmp", "cp"},
        "canyon": {"canyn", "canyon", "cnyn", "cyn"},
        "cape": {"cape", "cpe"},
        "causeway": {"causeway", "causwa", "causway", "cswy"},
        "center": {
            "cen",
            "cent",
            "center",
            "centr",
            "centre",
            "cnter",
            "cntr",
            "ctr",
        },
        "centers": {"centers", "ctrs"},
        "circle": {"ci", "cir", "circ", "circl", "circle", "crcl", "crcle"},
        "circles": {"circles", "cirs"},
        "cliff": {"clf", "cliff"},
        "cliffs": {"clfs", "cliffs"},
        "club": {"clb", "club"},
        "common": {"cmn", "common"},
        "commons": {"cmns", "commons"},
        "corner": {"cr", "cor", "corner"},
        "corners": {"corners", "cors"},
        "course": {"course", "crse"},
        "court": {"court", "crt", "ct"},
        "courts": {"courts", "cts"},
        "cove": {"cove", "cv"},
        "coves": {"coves", "cvs"},
        "creek": {"ck", "creek", "crk"},
        "crescent": {
            "crecent",
            "cres",
            "crescent",
            "cresent",
            "crscnt",
            "crsent",
            "crsnt",
        },
        "crest": {"crest", "crst"},
        "crossing": {"crossing", "crssing", "crssng", "xing"},
        "crossroad": {"crossroad", "xrd"},
        "crossroads": {"crossroads", "xrds"},
        "curve": {"curv", "curve"},
        "dale": {"dale", "dl"},
        "dam": {"dam", "dm"},
        "divide": {"div", "divide", "dv", "dvd"},
        "drive": {"dr", "driv", "drive", "drv"},
        "drives": {"drives", "drs"},
        "estate": {"est", "estate"},
        "estates": {"estates", "ests"},
        "expressway": {
            "exp",
            "expr",
            "express",
            "expressway",
            "expw",
            "expwy",
            "expy",
        },
        "extension": {"ext", "extension", "extn", "extnsn"},
        "extensions": {"extensions", "exts"},
        "fall": {"fall"},
        "falls": {"falls", "fls"},
        "ferry": {"ferry", "frry", "fry"},
        "field": {"field", "fld"},
        "fields": {"fields", "flds"},
        "flat": {"flat", "flt"},
        "flats": {"flats", "flts"},
        "ford": {"ford", "frd"},
        "fords": {"fords", "frds"},
        "forest": {"forest", "forests", "frst"},
        "forge": {"forg", "forge", "frg"},
        "forges": {"forges", "frgs"},
        "fork": {"fork", "frk"},
        "forks": {"forks", "frks"},
        "fort": {"fort", "frt", "ft"},
        "freeway": {"freeway", "freewy", "frway", "frwy", "fwy"},
        "garden": {"garden", "gardn", "gdn", "grden", "grdn"},
        "gardens": {"gardens", "gdns", "grdns"},
        "gateway": {"gateway", "gatewy", "gatway", "gtway", "gtwy"},
        "glen": {"glen", "gln"},
        "glens": {"glens", "glns"},
        "green": {"green", "grn"},
        "greens": {"greens", "grns"},
        "grove": {"grov", "grove", "grv"},
        "groves": {"groves", "grvs"},
        "harbor": {"harb", "harbor", "harbr", "hbr", "hrbor"},
        "harbors": {"harbors", "hbrs"},
        "haven": {"haven", "hvn", "havn"},
        "heights": {"heights", "hts", "hgts", "ht"},
        "highway": {"highway", "highwy", "hiway", "hiwy", "hway", "hwy"},
        "hill": {"hill", "hl"},
        "hills": {"hills", "hls"},
        "hollow": {"hllw", "hollow", "hollows", "holw", "holws"},
        "inlet": {"inlet", "inlt"},
        "island": {"is", "island", "islnd"},
        "islands": {"islands", "islnds", "iss"},
        "isle": {"isle"},
        "isles": {"isles"},
        "junction": {"jct", "jction", "jctn", "junction", "junctn", "juncton"},
        "junctions": {"jcts", "jctns", "junctions"},
        "key": {"key", "ky"},
        "keys": {"keys", "kys"},
        "knoll": {"knl", "knol", "knoll"},
        "knolls": {"knls", "knolls"},
        "lake": {"lake", "lk"},
        "lakes": {"lakes", "lks"},
        "land": {"land"},
        "landing": {"landing", "lndg", "lndng"},
        "lane": {"la", "lane", "ln"},
        "lanes": {"lanes", "lns"},
        "light": {"lgt", "light"},
        "lights": {"lgts", "lights"},
        "loaf": {"lf", "loaf"},
        "lock": {"lck", "lock"},
        "locks": {"lcks", "locks"},
        "lodge": {"ldg", "ldge", "lodg", "lodge"},
        "loop": {"loop", "lp"},
        "loops": {"loops", "lps"},
        "mall": {"mall"},
        "manor": {"manor", "mnr"},
        "manors": {"manors", "mnrs"},
        "meadow": {"mdw", "meadow"},
        "meadows": {"mdws", "meadows", "medows"},
        "mews": {"mews"},
        "mill": {"mill", "ml"},
        "mills": {"mills", "mls"},
        "mission": {"mission", "msn", "missn", "mssn"},
        "motorway": {"motorway", "mtwy"},
        "mount": {"mount", "mt"},
        "mountain": {"mountain", "mountin", "mntain", "mntn", "mtin", "mtn", "mn"},
        "mountains": {"mountains", "mntns", "mtns", "mtins", "mns"},
        "neck": {"nck", "neck"},
        "orchard": {"orch", "orchard", "orchrd"},
        "overlook": {"overlook", "ovlkn", "ovlk", "overlk", "olk"},
        "oval": {"oval", "ovl"},
        "overpass": {"opas", "overpass"},
        "park": {"park", "prk"},
        "parks": {"park", "parks"},
        "parkway": {"parkway", "parkwy", "pkway", "pkwy", "pky", "pw", "pwy"},
        "parkways": {"parkways", "pkwys"},
        "pass": {"pass"},
        "passage": {"passage", "psge"},
        "path": {"path"},
        "paths": {"paths"},
        "pike": {"pike", "pk"},
        "pikes": {"pikes", "pks"},
        "pine": {"pine", "pne"},
        "pines": {"pines", "pnes"},
        "place": {"pl", "place"},
        "plain": {"plain", "pln"},
        "plains": {"plaines", "plains", "plns"},
        "plaza": {"plaza", "plz", "plza"},
        "point": {"point", "pt"},
        "points": {"points", "pts"},
        "port": {"port", "prt"},
        "ports": {"ports", "prts"},
        "prairie": {"pr", "prairie", "prarie", "prr"},
        "radial": {"rad", "radial", "radiel", "radl"},
        "ramp": {"ramp"},
        "ranch": {"ranch", "rnch"},
        "ranches": {"ranches", "rnchs"},
        "rapid": {"rapid", "rpd"},
        "rapids": {"rapids", "rpds"},
        "rest": {"rest", "rst"},
        "ridge": {"rdg", "rdge", "ridge", "ri"},
        "ridges": {"rdgs", "ridges"},
        "river": {"riv", "river", "rivr", "rvr"},
        "road": {"rd", "road"},
        "roads": {"rds", "roads"},
        "route": {"route", "rte"},
        "row": {"row"},
        "rue": {"rue"},
        "run": {"run", "rn"},
        "shoal": {"shl", "shoal"},
        "shoals": {"shls", "shoals"},
        "shore": {"shore", "shr", "shoar"},
        "shores": {"shores", "shrs", "shoars"},
        "skyway": {"skwy", "skyway"},
        "spring": {"spg", "spng", "spring", "sprng"},
        "springs": {"spgs", "spngs", "springs", "sprngs"},
        "spur": {"spur"},
        "spurs": {"spurs"},
        "square": {"sq", "sqr", "sqre", "squ", "square"},
        "squares": {"sqs", "squares", "sqrs"},
        "station": {"sta", "station", "statn", "stn"},
        "strasse": {"strasse"},
        "stravenue": {
            "stra",
            "strav",
            "straven",
            "stravenue",
            "stravn",
            "strvn",
            "strvnue",
        },
        "stream": {"stream", "streme", "strm"},
        "street": {"st", "str", "street", "strt"},
        "streets": {"streets", "sts"},
        "summit": {"smt", "sumit", "sumitt", "summit"},
        "terrace": {"ter", "terr", "terrace"},
        "throughway": {"throughway", "trwy"},
        "trace": {"trace", "traces", "trce"},
        "track": {"track", "tracks", "trak", "trk", "trks"},
        "trafficway": {"trafficway", "trfy"},
        "trail": {"trail", "trl", "tr"},
        "trails": {"trails", "trls"},
        "trailer": {"trailer", "trlr"},
        "trailers": {"trailers", "trlrs"},
        "tunnel": {"tunel", "tunl", "tunnel", "tunnl", "tl"},
        "tunnels": {"tunnels", "tunls"},
        "turnpike": {"tpke", "trnpk", "turnpike", "turnpk", "tpk", "trpk"},
        "underpass": {"underpass", "upas"},
        "union": {"un", "union"},
        "unions": {"unions", "uns"},
        "valley": {"valley", "vally", "vlly", "vly"},
        "valleys": {"valleys", "vlys"},
        "via": {"via"},
        "viaduct": {"vdct", "via", "viadct", "viaduct"},
        "view": {"view", "vw"},
        "views": {"views", "vws"},
        "village": {"vill", "villag", "village", "villg", "villiage", "vlg"},
        "villages": {"villages", "vlgs"},
        "ville": {"ville", "vl"},
        "vista": {"vis", "vist", "vista", "vst", "vsta"},
        "walk": {"walk"},
        "walks": {"walks"},
        "wall": {"wall"},
        "way": {"way", "wy"},
        "well": {"well", "wl"},
        "wells": {"wells", "wls"},
    }


    @staticmethod
    def expand_street_type(
        value: str, street_names: dict[str, set[str]], discriminator: float = 97.0
    ) -> str:
        """
        Expand a potentially abbreviated or misspelled street type to its full form.
        Reference: https://www.urisa.org/clientuploads/directory/GMI/Professional%20Practice/Address%20Standard/AddressStandard_Approved_Apr11_03Class.pdf
                https://en.wikipedia.org/wiki/Street_suffix
        Args:
            value (str): The input street type to expand.
            street_names (Dict[str, Set[str]]): A dictionary mapping street type keys to sets of alternative spellings.
            discriminator (float, optional): The similarity threshold above which a match is considered. Default is 97.0.
        Returns:
            str: The expanded street type if a match is found, else the original value.
        """
        value = value.lower()

        if value in street_names:
            return value

        candidates = [
            (key, val)
            for key, val in street_names.items()
            if process.extractOne(value, val, scorer=fuzz.WRatio)[1]
            > discriminator
        ]
        return max(
            candidates,
            key=lambda x: process.extractOne(value, x[1], scorer=fuzz.WRatio)[1],
            default=(value,),
        )[0]


    @classmethod
    def parse_address(cls, address: str, w_street_expansion: bool = True) -> tuple[dict[str, str], str]:
        """Standardize an address using the usaddress package.
        Args:
            address (str): The address to standardize.
            w_street_expansion (bool, optional): Whether to expand the street type. Defaults to True.
        Returns:
            The parsed address and address type.
        """

        punctuation_to_remove = punctuation.replace('-', '')
        translation_table = str.maketrans('', '', punctuation_to_remove)
        address = address.translate(translation_table)
        
        # Clean the address text
        address = re.sub(r"[\r\n]+", " ", address)
        address = re.sub(r"\s+", " ", address).strip().lower()

        default_tagging, address_type = tag(address)

        if w_street_expansion:
            if street_name_post_type := default_tagging.get("StreetNamePostType", None):
                default_tagging["StreetNamePostType"] = cls.expand_street_type(
                    street_name_post_type, cls.US_STREET_NAMES
                )

        return default_tagging, address_type
    
    
    @staticmethod
    def parsed_to_str(address):
        addr_str = ""
        for _, v in address[0].items():
            addr_str += f"{v} "
        return addr_str[:-1]
    
    @classmethod
    def parsed_as_addr(cls, addr):
        if not addr or not addr[0]:
            return None
        
        addr=addr[0]

        zip_code = addr.get('ZipCode')
        if zip_code and len(zip_code) == 9:
            addr['ZipCode'] = f"{zip_code[:5]}-{zip_code[5:]}"

        if len(addr.get('StateName')) > 2:
            state_abbv = cls.STATE_FULL_TO_ABV[addr.get('StateName').title()]
            addr['StateCode'] = cls.STATE_TO_CODE[state_abbv]
        else:
            addr['StateCode'] = cls.STATE_TO_CODE[addr.get('StateName').upper()]
        addr['FullStreetName'] = (cls.build_street_name(addr))
        addr['StreetNumAndName'] = f"{addr['AddressNumber'].upper()} {addr['FullStreetName']}"
        secondary = cls.build_apt(addr)
        if secondary:
            secondary = secondary.strip()[:-1]
            addr['SecondaryAddress'] = secondary

        #full address with apartment and punctuation
        addr['FullAddress'] = (f"{addr.get('StreetNumAndName')}, {cls.build_apt(addr) if secondary else ''}{addr.get('PlaceName').title()}, {addr.get('StateName').upper()} {addr.get('ZipCode') if addr.get('ZipCode') else ''}").strip()

        #full address with apartment and no punctuation
        punctuation_to_remove = punctuation.replace('-', '')
        translation_table = str.maketrans('', '', punctuation_to_remove)
        addr['FullSearchable'] = addr['FullAddress'].translate(translation_table).strip()

        #can search OSM with this one
        addr['OsmSearchable'] = (f"{addr.get('StreetNumAndName')}, {addr.get('PlaceName').title()}, {addr.get('StateName').upper()} {addr.get('ZipCode') if addr.get('ZipCode') else ''}").strip()
        
        return addr
    
    @staticmethod
    def build_apt(addr):
        if not addr.get('OccupancyIdentifier'):
            return None
        if addr.get('OccupancyType'):
            return f"{addr.get('OccupancyType', '')} {addr.get('OccupancyIdentifier', '')}, ".title()
        return f"#{addr.get('OccupancyIdentifier', '')}, ".title()

    @staticmethod
    def build_street_name(addr):
        parts = [
            addr.get('StreetNamePreDirectional', '').upper() if addr.get('StreetNamePreDirectional') else None,
            addr.get('StreetNamePreType').title() if addr.get('StreetNamePreType') else None,
            addr.get('StreetName').title() if addr.get('StreetName') and not addr.get('StreetName')[0].isdigit() else addr.get('StreetName'),            
            addr.get('StreetNamePostType').title() if addr.get('StreetNamePostType') else None,
            addr.get('StreetNamePostDirectional', '').upper() if addr.get('StreetNamePostDirectional') else None
        ]
        # Filter out None values and join the parts with a space
        return ' '.join(filter(None, parts)).strip()
    
    @staticmethod
    def parsed_street_to_model(model, addr):
        model.housenumber = addr[0]['AddressNumber']
        model.street = f"{addr[0]['StreetName'].capitalize()} {addr[0]['StreetNamePostType'].capitalize() if 'StreetNamePostType' in addr[0].keys() else ''}"
        return model
    
""" Usage
address = "123 Test St, Testville, TX 12345, USA"
parsed_address = AddressNormalization.parse_address(address)
print(parsed_address)
parsed_address == (OrderedDict({
        'AddressNumber': '123', 
        'StreetName': 'test', 
        'StreetNamePostType': 'street', 
        'PlaceName': 'testville', 
        'StateName': 'tx', 
        'ZipCode': '12345', 
        'CountryName': 'usa'
    }), 'Street Address')
"""
