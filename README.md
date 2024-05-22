# Скрипт для сортировки скринов EMS
![example.png](https://github.com/Slayez/emsreader/blob/master/img/example.png)
![example2.png](https://github.com/Slayez/emsreader/blob/master/img/example2.png)
# https://pytorch.org
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install easyocr
pip install Pillow
pip install shutil
```

Если у вас формат экрана отличается от стандартного.

Исправьте вручную данную строку, всё в % соотношении.
```
im_crop = im.crop((im.size[0]*0.16, im.size[1]*0.83, im.size[0]*0.65, im.size[1]));
```
