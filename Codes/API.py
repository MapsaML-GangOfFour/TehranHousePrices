from enum import Enum
from pickle import load
from fastapi import FastAPI, Query

# 'uvicorn API:app --reload' in cmd to run host
app = FastAPI()
with open('../data/Zones.pkl', 'rb') as file:
    zone = load(file, encoding="utf-8")
AreaEnum = Enum('نواحی تهران', zip(zone, zone), type=str)
yes_no_txt = ['No', 'Yes']
yes_no_fa = ['خیر', 'بله']
YesNo = Enum('YesNo', zip(yes_no_txt, yes_no_fa), start=0)


@app.get("/")
async def root(
        *,
        district: AreaEnum = Query(..., alias="محله", description="آپارتمان در کدام محله تهران واقع است؟", ),
        floor: int = Query(..., alias="طبقه واحد",
                           description="شماره طبقه واحد به صورتی که همکف برابر صفر و واحد منفی 60 برابر 1- است", ),
        year: str = Query(..., alias="سال ساخت", description="سال ساخت به صورت چهار رقمی وارد شود", regex=r'1[34][\d]{2}'),
        rooms: int = Query(None, alias="تعداد اتاق", description="تعداد اتاق های مستقل موجود در واحد"),
        area: int = Query(None, alias="متراژ", description="زیر بنای مفید واحد"),
        elevator: YesNo = Query(..., alias="آسانسور", description="آیا ساختمان دارای آسانسور است", ),
        park: YesNo = Query(..., alias="پارکینگ", description="آیا واحد دارای پارکینگ اختصاصی هست", ),
        storage: YesNo = Query(..., alias="انباری", description="آیا واحد دارای انباری مستقل هست", ),
        ):
    return {"AreaEnum": district,
            'area'    : area,
            'elevator': elevator == YesNo.Yes}
