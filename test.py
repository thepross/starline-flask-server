import cv2
import numpy as np

def scale(image, scale_width):
    (image_height, image_width) = image.shape[:2]
    new_height = int(scale_width / image_width * image_height)
    return cv2.resize(image, (scale_width, new_height))

# logo = cv2.imread('images/logo3.png')
# # img = cv2.imread('images/image.jpg')
# img = scale(cv2.imread('images/image.jpg'), 800)

# filas, columnas, canales = logo.shape
# width, height, channels = img.shape

# # img[0:filas, 0:columnas] = logo

# # interactuar entre imagenes iguales
# roi = img[0:filas, 0:columnas] # arriba izquierda
# # roi = img[width-filas:width, 0:columnas] # abajo izquierda
# # roi = img[0:filas, height-columnas:height] # arriba derecha
# # roi = img[width - filas:width, height - columnas:height] # abajo derecha
# cv2.imshow("roi", roi)

# #binarizar el logo
# logo_gris = cv2.cvtColor(logo, cv2.COLOR_RGB2GRAY)
# ret, mascara = cv2.threshold(logo_gris, 190, 255, cv2.THRESH_BINARY)
# mascara_invertida = cv2.bitwise_not(mascara)

# #operaciones
# img_fondo = cv2.bitwise_and(roi, roi, mask=mascara)
# logo_frente = cv2.bitwise_and(logo, logo, mask=mascara_invertida)

# #combinar
# res = cv2.add(img_fondo, logo_frente)

# #añadir logo
# # img[0:filas, 0:columnas] = res
# img[width - filas:width, height - columnas:height] = res

# cv2.imshow("Resultado", img)


logo = cv2.imread('images/logo.png', cv2.IMREAD_UNCHANGED)
bgr = logo[:,:,:3] # Channels 0..2
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
alpha = logo[:,:,3] # Channel 3
result = np.dstack([bgr, alpha])
cv2.imwrite('51IgH_result.png', result)

cv2.waitKey(0)
cv2.destroyAllWindows()