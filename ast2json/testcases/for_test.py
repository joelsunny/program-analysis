# nested for loop
for i,v in enumerate([1,2,5,6]):
    for j in range(i):
        print(i,j)

async def get_result():
    return [1,2,3,4]

# async for loop
async for doc in get_result():
    pass