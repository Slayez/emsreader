# Скрипт для сортировки скринов EMS
![example.png](https://github.com/Slayez/emsreader/blob/master/img/example2.png)  
![example2.png](https://github.com/Slayez/emsreader/blob/master/img/example.png)
# https://pytorch.org
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install easyocr
pip install Pillow
pip install shutil
```
Для работы укажите папку для получения скринов и их сортировки (будут найдены все скрины во вложенных папках)
```
    # главная директория в которой будет создана сортировка, в ней должна быть папка со скринами
    MAIN_DIR = "D:/рп/EMS/";

    # папка со скринами
    path_img = MAIN_DIR+"NEW/";
```

Если у вас формат экрана отличается от стандартного.

Исправьте вручную данную строку, всё в % соотношении.
```
im_crop = im.crop((im.size[0]*0.16, im.size[1]*0.83, im.size[0]*0.65, im.size[1]));
```
