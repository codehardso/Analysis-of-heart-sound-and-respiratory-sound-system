from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import sys
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
import librosa
import time
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
from pydub import AudioSegment
import librosa, librosa.display
import samplerate
from scipy import signal
from tensorflow import keras
import numpy as np
from keras.models import Sequential, Model
import bg_res

class ProcessFunction(object):  ##这里负责写一些数字信号处理的方法
    def Audio_TimeDomain(self, feature):  ##时域
        file = feature.path
        audio, sample_rate = librosa.load(file, sr=None)
        feature.textBrowser.append("采样频率: " + str(sample_rate)+" Hz")
        seconds = (len(audio) - 1) / sample_rate
        newsec = round(seconds,2)
        feature.textBrowser.append("文件时长" + str(newsec)+" 秒")
        feature.progressBar.setValue(10)

        feature.fig.clear()

        ax = feature.fig.add_subplot(111)
        #调整图像大小
        ax.cla()  #
        #time = (1.0 /sample_rate ) * (1:len(audio));
        time = np.arange(0, len(audio)) * (1.0 /sample_rate)# 最后通过采样点数和取样频率计算出每个取样的时间
        #librosa.display.waveplot(signal, sample_rate, alpha=0.4)
        ax.plot(time, audio)
        ax.set_title("Waveform")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(color='0.7', linestyle='--', linewidth=1)
        #feature.fig.subplots_adjust(left=None, bottom=0.2, right=None, top=None, wspace=None, hspace=None)
        feature.canvas.draw()  # TODO:这里开始绘制

        feature.progressBar.setValue(20)

        fft = np.fft.fft(audio)
        # calculate abs values on complex numbers to get magnitude
        spectrum = np.abs(fft)

        # create frequency variable
        f = np.linspace(0, sample_rate, len(spectrum))

        # take half of the spectrum and frequency
        left_spectrum = spectrum[:int(len(spectrum) / 2)]
        left_f = f[:int(len(spectrum) / 2)]

        feature.progressBar.setValue(30)

        feature.fig2.clear()
        ax = feature.fig2.add_subplot(111)
        #feature.fig2.subplots_adjust(left=None, bottom=0.2, right=None, top=None, wspace=None, hspace=None)
        ax.cla()  # TODO:删除原图，让画布上只有新的一次的图

        ax.set_title('Power spectrum')
        ax.plot(left_f, left_spectrum, alpha=0.4)
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Magnitude')
        ax.grid(color='0.7', linestyle='--', linewidth=1)
        feature.canvas2.draw()  # TODO:这里开始绘制
        feature.progressBar.setValue(40)

    def Audio_FrequencyDomain(self,feature):
        file = feature.path
        audio, sample_rate = librosa.load(file, sr=None)
        # STFT -> spectrogram
        hop_length = 512  # in num. of samples
        n_fft = 2048  # window in num. of samples

        # calculate duration hop length and window in seconds
        hop_length_duration = float(hop_length) / sample_rate
        n_fft_duration = float(n_fft) / sample_rate
        print("STFT hop length duration is: {}s".format(hop_length_duration))
        print("STFT window duration is: {}s".format(n_fft_duration))

        feature.fig4.clear()

        feature.progressBar.setValue(50)
        # perform stft
        stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)

        # calculate abs values on complex numbers to get magnitude
        spectrogram = np.abs(stft)

        # apply logarithm to cast amplitude to Decibels
        log_spectrogram = librosa.amplitude_to_db(spectrogram)
        ax = feature.fig4.subplots()
        img = librosa.display.specshow(log_spectrogram,sr=sample_rate, hop_length=hop_length, ax=ax, x_axis="time")
        ax.set_title("Spectrogram (dB)")
        ax.set_ylabel("Frequency")
        plt.colorbar(img, ax=ax, format="%+2.0f dB")

        feature.canvas4.draw()  # TODO:这里开始绘制
        feature.progressBar.setValue(60)

    def Audio_MFCCs(self,feature):
        # MFCCs
        # extract 13 MFCCs
        file = feature.path
        audio, sample_rate = librosa.load(file, sr=None)
        hop_length = 512  # in num. of samples
        n_fft = 2048  # window in num. of samples

        feature.fig3.clear()
        # calculate duration hop length and window in seconds
        hop_length_duration = float(hop_length) / sample_rate
        n_fft_duration = float(n_fft) / sample_rate
        MFCCs = librosa.feature.mfcc(audio, sample_rate, n_fft=n_fft, hop_length=hop_length, n_mfcc=13)
        feature.progressBar.setValue(70)
        # display MFCCs

        ax = feature.fig3.subplots()
        img = librosa.display.specshow(MFCCs, sr=sample_rate, hop_length=hop_length, ax=ax, x_axis="time")
        ax.set_ylabel("MFCC coefficients")
        ax.set_title("MFCCs")
        plt.colorbar(img, ax=ax)
        feature.canvas3.draw()  # TODO:这里开始绘制
        feature.progressBar.setValue(80)

    def melspectrogram(self, feature):
        feature.fig5.clear()
        file = feature.path
        audio, sample_rate = librosa.load(file, sr=None)
        D = np.abs(librosa.stft(audio)) ** 2

    # Passing through arguments to the Mel filters
        S = librosa.feature.melspectrogram(y=audio, sr=sample_rate, n_mels=128,fmax=8000)
        ax = feature.fig5.subplots()
        S_dB = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(S_dB, x_axis='time',
                                   y_axis='mel', sr=sample_rate,
                                   fmax=8000, ax=ax)
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        ax.set(title='Mel-frequency spectrogram')
        feature.canvas5.draw()

    def s_contrast(self,feature):
        file = feature.path
        feature.fig6.clear()
        audio, sample_rate = librosa.load(file, sr=None)
        S = np.abs(librosa.stft(audio))
        contrast = librosa.feature.spectral_contrast(S=S, sr=sample_rate)

        ax = feature.fig6.subplots(2,1)
        img1 = librosa.display.specshow(librosa.amplitude_to_db(S,
                                                                ref=np.max),
                                        y_axis='log', x_axis='time', ax=ax[0])
        plt.colorbar(img1, ax=[ax[0]], format='%+2.0f dB')
        ax[0].set(title='Power spectrogram')
        ax[0].label_outer()
        img2 = librosa.display.specshow(contrast, x_axis='time', ax=ax[1])
        plt.colorbar(img2, ax=[ax[1]])
        ax[1].set(ylabel='Frequency bands', title='Spectral contrast')

        feature.canvas6.draw()

    def tonnetz(self,feature):
        file = feature.path
        feature.fig7.clear()
        audio, sample_rate = librosa.load(file, sr=None)
        y = librosa.effects.harmonic(audio)
        tonnetz = librosa.feature.tonnetz(y=audio, sr=sample_rate)

        ax = feature.fig7.subplots(2,1)
        img1 = librosa.display.specshow(tonnetz,
                                        y_axis='tonnetz', x_axis='time', ax=ax[0])
        ax[0].set(title='Tonal Centroids (Tonnetz)')
        ax[0].label_outer()
        img2 = librosa.display.specshow(librosa.feature.chroma_cqt(y=audio, sr=sample_rate),
                                        y_axis='chroma', x_axis='time', ax=ax[1])
        ax[1].set(title='Chroma')
        plt.colorbar(img1, ax=[ax[0]])
        plt.colorbar(img2, ax=[ax[1]])

        feature.canvas7.draw()

    def Model_Apply(self, feature):
        model = keras.models.load_model("model/rsd_5.h5")
        file = feature.path
        audio, sample_rate = librosa.load(file, sr=None)
        fs = sample_rate
        print("file",file)

        def audio_features(filename):
            sound, sample_rate = librosa.load(filename)
            stft = np.abs(librosa.stft(sound))

            mfccs = np.mean(librosa.feature.mfcc(y=sound, sr=sample_rate, n_mfcc=40), axis=1)
            chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate), axis=1)
            mel = np.mean(librosa.feature.melspectrogram(sound, sr=sample_rate), axis=1)
            contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate), axis=1)
            tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(sound), sr=sample_rate), axis=1)

            concat = np.concatenate((mfccs, chroma, mel, contrast, tonnetz))
            return concat

        def data_points():
            images = []
            images.append(audio_features(file))

            return np.array(images)

        def preprocessing(images):
            test_images = np.reshape(images, (images.shape[0], images.shape[1], 1))
            return test_images

        images = data_points()
        test_images = preprocessing(images)
        feature.progressBar.setValue(90)
        predictions = model.predict(test_images)
        classpreds = np.argmax(predictions, axis=1)  # predicted classes
        matrix_index = ["COPD", "Healthy", "URTI", "Bronchiectasis", "Pneumoina", "Bronchiolitis"]
        name = ["慢性阻塞性肺疾病", "健康", "上呼吸道感染", "支气管扩张", "肺炎", "细支气管炎"]
        # print("Result:结果"+ matrix_index[int(classpreds)])
        # print(f"结果是：{matrix_index[int(classpreds)]}")
        print(f"Result:{matrix_index[int(classpreds)]}")
        feature.textBrowser.append(f"识别结果为:{name[int(classpreds)]}")


class Resp(QMainWindow):
    def __init__(self):
        super(Resp, self).__init__()
        loadUi("ui_file/RespiratoryCare.ui", self)
        self.Process = ProcessFunction()

        self.label = self.findChild(QLabel, "label")
        self.textBrowser = self.findChild(QTextBrowser, "textBrowser")
        self.play = self.findChild(QPushButton, "play")
        self.analysis = self.findChild(QPushButton, "analysis")
        self.progressBar = self.findChild(QProgressBar, "progressBar")
        self.slider = self.findChild(QSlider, "horizontalSlider")
        self.label_2 = self.findChild(QLabel, "label_2")
        self.label_3 = self.findChild(QLabel, "label_3")
        self.action_2 = self.findChild(QAction, "action_2")
        self.action_3 = self.findChild(QAction, "action_3")
        self.pushButton = self.findChild(QPushButton, "pushButton")
        self.pushButton_2 = self.findChild(QPushButton, "pushButton_2")
        self.pushButton_3 = self.findChild(QPushButton, "pushButton_3")
        self.pushButton_4 = self.findChild(QPushButton, "pushButton_4")
        self.label_4 = self.findChild(QLabel, "label_4")
        self.pushButton_5 = self.findChild(QPushButton, "openButton")

        self.timeButton = self.findChild(QPushButton, "timeButton")
        self.spectrumButton = self.findChild(QPushButton, "spectrumButton")
        self.spectrogramButton = self.findChild(QPushButton, "spectrogramButton")
        self.mfccButton = self.findChild(QPushButton, "mfccButton")
        self.stackedWidget = self.findChild(QStackedWidget, "stackedWidget")

        self.stackedWidget.setCurrentWidget(self.page)

        self.melspectroButton = self.findChild(QPushButton, "melspectroButton")
        self.contrastButton = self.findChild(QPushButton, "contrastButton")
        self.tonnetzButton = self.findChild(QPushButton, "tonnetzButton")


        self.progressBar.setValue(0)  # 进度条初始化为0
        # ***************标志位的初始化*******************
        self.process_flag = 0  # 处理完毕标志位
        self.isPlay = 0  # 播放器播放标志位
        self.player = QMediaPlayer(self)
        self.horizontalSlider.sliderMoved[int].connect(lambda: self.player.setPosition(self.horizontalSlider.value()))
        self.horizontalSlider.setStyle(QStyleFactory.create('Fusion'))

        self.timer = QTimer(self)
        self.timer.start(1000)##定时器设定为1s，超时过后链接到playRefresh刷新页面
        self.timer.timeout.connect(self.playRefresh)##

        self.Timelayout_()  ##时间域的四个图窗布局
        # Do something
        #self.button.clicked.connect(self.clicker)
        #self.clear_button.clicked.connect(self.clearer)
        #self.action_2.triggered.connect(self.onFileOpen)  ##菜单栏的action打开文件
        #self.action_3.triggered.connect(self.close)  # 菜单栏的退出action
        self.play.clicked.connect(self.palyMusic)
        self.analysis.clicked.connect(self.Analyse_btn_start)
        self.pushButton.clicked.connect(self.volumeDown)
        self.pushButton_2.clicked.connect(self.volumeUp)
        #self.pushButton_3.clicked.connect(self.openmp3file)
        #self.pushButton_4.clicked.connect(self.mp32wav)
        self.pushButton_5.clicked.connect(self.onFileOpen)

        self.timeButton.clicked.connect(self.showTime)
        self.spectrumButton.clicked.connect(self.showSP)
        self.spectrogramButton.clicked.connect(self.showSPEC)
        self.mfccButton.clicked.connect(self.showMfcc)

        self.melspectroButton.clicked.connect(self.melspectrogram)
        self.contrastButton.clicked.connect(self.showcontrast)
        self.tonnetzButton.clicked.connect(self.showtonnetz)

        # Show The App
        self.show()

    def showTime(self):
        self.stackedWidget.setCurrentWidget(self.page)

    def showSP(self):
        self.stackedWidget.setCurrentWidget(self.page_2)

    def showSPEC(self):
        self.stackedWidget.setCurrentWidget(self.page_4)

    def showMfcc(self):
        self.stackedWidget.setCurrentWidget(self.page_3)

    def melspectrogram(self):
        self.stackedWidget.setCurrentWidget(self.page_5)

    def showcontrast(self):
        self.stackedWidget.setCurrentWidget(self.page_6)

    def showtonnetz(self):
        self.stackedWidget.setCurrentWidget(self.page_7)




    def Timelayout_(self):
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout()  # 垂直布局
        layout.addWidget(self.canvas)
        self.graphicsView.setLayout(layout)  # 设置好布局之后调用函数

        self.fig2 = plt.figure()
        self.canvas2 = FigureCanvas(self.fig2)
        layout = QVBoxLayout()  # 垂直布局
        layout.addWidget(self.canvas2)
        self.graphicsView_2.setLayout(layout)  # 设置好布局之后调用函数

        self.fig3 = plt.Figure()
        self.canvas3 = FigureCanvas(self.fig3)
        layout = QVBoxLayout()  # 垂直布局
        layout.addWidget(self.canvas3)
        self.graphicsView_3.setLayout(layout)  # 设置好布局之后调用函数

        self.fig4 = plt.Figure()
        self.canvas4 = FigureCanvas(self.fig4)
        layout = QVBoxLayout()  # 垂直布局
        layout.addWidget(self.canvas4)
        self.graphicsView_4.setLayout(layout)  # 设置好布局之后调用函数

        self.fig5 = plt.Figure()
        self.canvas5 = FigureCanvas(self.fig5)
        layout = QVBoxLayout()  # 垂直布局
        layout.addWidget(self.canvas5)
        self.graphicsView_5.setLayout(layout)  # 设置好布局之后调用函数

        self.fig6 = plt.Figure()
        self.canvas6 = FigureCanvas(self.fig6)
        layout = QVBoxLayout()  # 垂直布局
        layout.addWidget(self.canvas6)
        self.graphicsView_6.setLayout(layout)  # 设置好布局之后调用函数

        self.fig7 = plt.Figure()
        self.canvas7 = FigureCanvas(self.fig7)
        layout = QVBoxLayout()  # 垂直布局
        layout.addWidget(self.canvas7)
        self.graphicsView_7.setLayout(layout)  # 设置好布局之后调用函数

    def onFileOpen(self): ##打开文件
        self.path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', '音乐文件 (*.wav);;音乐文件(*.mp3)')

        if self.path:##选中文件之后就选中了需要播放的音乐，并同时显示出来
            self.isPlay=0#每次打开文件的时候就需要暂停播放，无论是否在播放与否

            self.player.pause()

            self.player.setMedia(QMediaContent(QUrl(self.path)))  ##选中需要播放的音乐
            self.horizontalSlider.setMinimum(0)
            self.horizontalSlider.setMaximum(self.player.duration())
            self.horizontalSlider.setValue(self.horizontalSlider.value() + 1000)
            self.horizontalSlider.setSliderPosition(0)

            self.label.setText("当前文件名为:  "+os.path.basename(self.path))

    def palyMusic(self):
        try:
            if self.path:#这个path是当前的路径，如果path变了，那么就意味着更换了文件
                if not self.isPlay:##如果isPaly=0，那就说明播放器并没有打开，且此时按下了播放按钮，就开始播放
                    self.player.play()
                    self.isPlay=1##播放之后同时置为1，代表播放器目前正在播放
                else:
                    self.player.pause()
                    self.isPlay = 0  ##暂停之后同时置为0，代表播放器目前没有播放
        except Exception as e:
            print(e)
            self.textBrowser_2.setText("There are some errors occuring when playing audio")

    def playRefresh(self):
        if self.isPlay:
            # print(self.player.duration())
            self.horizontalSlider.setMinimum(0)
            self.horizontalSlider.setMaximum(self.player.duration())
            self.horizontalSlider.setValue(self.horizontalSlider.value() + 1000)
        # ORIGINAL AUDIO
        self.label_2.setText(time.strftime('%M:%S', time.localtime(self.player.position() / 1000)))
        self.label_3.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))

    def volumeUp(self):
        currentVolume = self.player.volume() #
        print(currentVolume)
        self.player.setVolume(currentVolume + 5)

    def volumeDown(self):
        currentVolume = self.player.volume() #
        print(currentVolume)
        self.player.setVolume(currentVolume - 5)

    def Analyse_btn_start(self):##这里对应的是打开文件，并点击按钮
        try:
            if self.path:##要必须在打开文件之后才允许进行处理
                self.textBrowser.append(str(time.strftime("%Y %m %d %H:%M:%S", time.localtime())) )
                self.textBrowser.append("当前文件名 :"+str(os.path.basename(self.path)))
                self.progressBar.setValue(0)  ##每次允许处理时进度条归0
                self.Process.Audio_TimeDomain(self)  ##把实例传入进去
                self.Process.Audio_FrequencyDomain(self)
                self.Process.Audio_MFCCs(self)
                self.Process.melspectrogram(self)
                self.Process.s_contrast(self)
                self.Process.tonnetz(self)
                self.Process.Model_Apply(self)
                self.progressBar.setValue(100)
                self.textBrowser.append("分析成功!")


        except Exception as e:
            print(e)
            self.textBrowser.setText("There are some errors occuring when programme trying to open file")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Resp()
    window.show()
    sys.exit(app.exec())