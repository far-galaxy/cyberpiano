# CyberPiano
- Простая Arduino Midi Клавиатура
- Работа в качестве Midi клавиатуры
- Работа в качестве синтезатора при помощи FluidSynth

## Файлы:
- cyberpiano.py - основная программа
- cyberpiano_old.py - старая версия на pygame
- cp_obj.py - модуль для старой версии
- fluidsynth.py - библиотека синтезатора
- /fluidsynth/libfluidsynth.dll - библиотека fluidsynth для Windows
- /soundfonts - банки звуков .sf2

## Туду:
- [x] Переписать фронтенд на Qt
- [ ] Добавить возможность аккомпанинирования при помощи Midi файлов
- [ ] Поковыряться с контейнерами
- [x] Встроить библиотеки 
- [x] Портировать программу для Windows 
- [x] Сделать возможность загружать другой банк, не перезапуская программу
- [x] Сделать переключение по каналам
- [x] ~~Добавить другие способы загрузки сэмплов, кроме SF2~~

## Инструкция по установке:

1. Установить PyQt5:
`pip install pyqt5`

2.Установить fluidsynth для Linux:

`sudo apt-get install fluidsynth`

##Запуск старой версии

1. Установить pygame:
`pip install pygame`

2. Установить mingus:
`pip install mingus`

3. Установить pyserial:
`pip install pyserial`

4. Установить fluidsynth:

**Linux:**

`sudo apt-get install fluidsynth`

**Windows:**

Закинуть файл libfluidsynth.dll в папку, где установлен Python


## Запуск синтезатора:

1. Закинуть нужные банки звуков в папку soundfonts

2. Запустить cyberpiano.py

3. Вверху выбрать порт, нажать "Connect" 

4. Проверить работу клавиатуры, нажав на клавишу, в окне "Information" должен отобразиться номер клавиши

5. Загрузить банк звуков, нажав "Open .sf2"

6. Выбрать инструмент во вкладке "Instrument"

7. Наслаждаться игрой
