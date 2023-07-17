
import requests
import os, random

def bk_img_retrieval(text, local_image_folder = "./bk_image_folder", estilo = 1):
    bk_path = local_image_folder + "/" + str(estilo)
    bk_rnd = random.choice(os.listdir(bk_path))
    image_path_list = [bk_path + "/" + bk_rnd]
    print(image_path_list)
    return image_path_list

    # API para acceder a los background o imagenes de fondo de cada elemento, 
    # Solo aplicamos de forma local de momento, hasta la siguiente implementacion de union o merge
    # de nuestro codigo para combinarlo con un servicio de API propio para la generacion de fondos, 
    # Este ya se encuentra disponible pero de forma local.

    # url = "http://URL/query"
    # response = requests.get(url, params={"text": text})
    # results = response.json()
    # print(results)
    '''
    Ejemplo: 
        {
            'data': 
            [
                {
                    'image_list': 
                    [
                        {'image_path': 'http://buling.wudaoai.cn/image_unzip/mtMFJz071Cs.png',
                        'image_url': 'https://unsplash.com/photos/mtMFJz071Cs'},
                        {'image_path': 'http://buling.wudaoai.cn/image_unzip/ZHS3j0_Y_KM.png',
                        'image_url': 'https://unsplash.com/photos/ZHS3j0_Y_KM'},
                    ],
                    'text': 'texto1。'
                },
            ],
            'info': 'sentence',
            'status_code': 2001,
            'work_id': 'bVAUkjVj3AP0A5aWZ7g07oey'
        }
    '''
    
    # net_files = [item["image_path"] for item in results["data"][0]["image_list"]]
    # unsplash_files = [item["image_url"] for item in results["data"][0]["image_list"]]
    # files = [item["image_path"].split("/")[-1] for item in results["data"][0]["image_list"]]
    # image_path_list = [local_image_folder + "/" + file for file in files]

    # for net_file, file, path, unsplash_path in zip(net_files, files, image_path_list, unsplash_files):
    #     if not os.path.exists(path):
    #         print("Download pictiure {} from {}".format(file, net_file))
    #         print("Pictiure {} Origin UNSPLASH path: {}".format(file, unsplash_path))
    #         r = requests.get(net_file)
    #         f = open(path, "wb")
    #         f.write(r.content)
    #         f.close()
    # return image_path_list


if __name__ == "__main__":
    text = "Texto 1"
    local_image_folder = "bk_image_folder"
    image_path_list = bk_img_retrieval(text, local_image_folder)
    print(image_path_list)
