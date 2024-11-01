from typing import Optional, Union
from pydantic import BaseModel, Field

class NewNominatimEntry(BaseModel):
    housenumber: Union[str|int]
    street: str
    postcode: Union[str|int]
    city: str
    state: str
    lat: float
    lon: float
    country: Optional[str] = Field(default="US")
    country_code: Optional[str] = Field(default="us")
    addresstype: Optional[str] = Field(default="residential")
    buildingtype: Optional[str] = Field(default="apartment")
    visible: Optional[bool] = Field(default=True)
    category: Optional[str] = Field(default="place")

    def create_full_str(self):
        return f"{self.housenumber} {self.street}, {self.state}, {self.country} {self.postcode}"
