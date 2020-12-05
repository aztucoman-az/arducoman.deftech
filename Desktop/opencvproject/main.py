from deepface import DeepFace
result  = DeepFace.verify("m1.jpg", "m2.jpg")
#results = DeepFace.verify([['img1.jpg', 'img2.jpg'], ['img1.jpg', 'img3.jpg']])
#print(result['distance'])
#print("Is verified: ", result['verified'])
print(result)
if (result['distance'])>= 0.2 :
    print('Oxsar Deyil')
else:
    print('Oxsardir')
