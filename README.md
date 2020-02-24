# CyberPiano
- Простая Arduino Midi Клавиатура
- Работа в Windows в качестве Midi клавиатуры
- Работа с Raspberry Pi и другими Linux-системами при помощи FluidSynth

## Туду:
- [ ] Дописать оболочку программы
- [x] ~~Добавить другие способы загрузки сэмплов, кроме SF2~~
- [ ] Добавить возможность аккомпанинирования при помощи Midi файлов
- [x] Портировать программу для Windows (FluidSynth работает на Винде коряво) 
- [ ] Сделать возможность загружать другой банк, не перезапуская программу

## Инструкция по установке:

1. Установить mingus:

`pip install mingus`

2. Установить fluidsynth:

**Linux:**

`sudo apt-get install fluidsynth`

**Windows:**

Закинуть содержимое папки fluidsynth в папку, где установлен Python
