Quasicrystal 圖片產生器
===

## 分段式 Quasicrystal 圖片產生器，Colab連結。

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/bombduck/AnimateQuasicrystal/blob/main/AnimateQuasiCrystal.ipynb)

## 本程式修改自 [QuasicrystalGifs](https://github.com/makeyourownmaker/QuasicrystalGifs)。雖然程式碼有些差異，但產生 quasicrystal 圖片、動態圖片和著色的原理並沒有改變。

### 程式的改變在於：
  1. 讓大部分未指定的參數隨機產生，每次執行都能產生不同圖片。
  2. 輸出上次執行的參數，可以把喜歡圖片的參數保留，或是保留部分，用來下次產生圖片。
  3. 加了一個漸進式參數變化的動畫。

### 專案分成兩個程式：
  1. Python 檔案，在 python 執行，可以一口氣亂數產生多個檔案。
  2. Jupyter Notebook 檔案，在 notebook 階段式執行，可以線上執行和實驗。

### Python 程式使用範例：
  1. 將 QuasicrystalGif.py(函式庫) 和 Generate.py(執行檔)。
  2. 確定必要的套件有安裝 (抱歉，這部分我還不知道怎麼幫忙。)
  3. 下指令 <i>python Generate.py -fd ../Graph -n 10</i>，會在上一層的 Graph 底下產生三十張圖片，十張靜態和二十張動態。

## 注意，程式碼是我自己寫的，但註解和說明靠 AI 產生後修飾。
