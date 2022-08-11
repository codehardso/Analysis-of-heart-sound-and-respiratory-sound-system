from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import sys
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
import time
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
from pydub import AudioSegment
import librosa
import librosa.display
import samplerate
from scipy import signal
from tensorflow import keras
import numpy as np

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
        feature.canvas.draw()

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
        ax.cla()

        ax.set_title('Power spectrum')
        ax.plot(left_f, left_spectrum, alpha=0.4)
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Magnitude')
        ax.grid(color='0.7', linestyle='--', linewidth=1)
        feature.canvas2.draw()
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

        feature.canvas4.draw()
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
        feature.canvas3.draw()
        feature.progressBar.setValue(80)

    def Model_Apply(self, feature):

        file = feature.path
        audio, sample_rate = librosa.load(file, sr=None)
        fs = sample_rate

        def band_pass_filter(original_signal, order, fc1, fc2, fs):
            b, a = signal.butter(N=order, Wn=[2 * fc1 / fs, 2 * fc2 / fs], btype='bandpass')
            new_signal = signal.lfilter(b, a, original_signal)
            return new_signal

        audio_data = band_pass_filter(audio, 2, 25, 400, fs)

        # 下采样
        down_sample_audio_data = samplerate.resample(audio_data.T, 1000 / fs, converter_type='sinc_best').T
        down_sample_audio_data = down_sample_audio_data / np.max(np.abs(down_sample_audio_data))

        # 切割
        total_num = len(down_sample_audio_data) / (2500)

        dataset = np.ones((1, 256, 256, 1))
        dataset = dataset.astype('float32')
        from extract_bispectrum import polycoherence, plot_polycoherence

        ex_audio_data = down_sample_audio_data[:2500]
        freq1, freq2, bi_spectrum = polycoherence(ex_audio_data, nfft=1024, nperseg=256, noverlap=100, fs=1000,
                                                  norm=None)
        bi_spectrum = np.array(abs(bi_spectrum))  # calculate bi_spectrum
        bi_spectrum = 255 * (bi_spectrum - np.min(bi_spectrum)) / (np.max(bi_spectrum) - np.min(bi_spectrum))
        # plot_polycoherence(freq1, freq2, bi_spectrum)
        # 修改尺寸以便于投入神经网络
        bi_spectrum = bi_spectrum.reshape((256, 256, 1))

        dataset = np.vstack((dataset, np.array([bi_spectrum])))
        dataset = np.delete(dataset, 0, 0)
        dataset = dataset.astype('float32')

        def shuffle_data_label(data):
            state = np.random.get_state()
            np.random.shuffle(data)
            np.random.set_state(state)
            return data

        img_data = shuffle_data_label(bi_spectrum)
        # data_f = float(img_data)
        t = type(bi_spectrum)
        print("tye=:/n", t)
        model = keras.models.load_model("model/model_5.h5")

        predictions = model.predict(dataset)
        name = ["正常", "主动脉瓣狭窄", "二尖瓣狭窄", "二尖瓣反流", "二尖瓣脱垂"]
        print('识别为：')
        print(name[np.argmax(predictions)])
        feature.textBrowser.append("识别为：" + name[np.argmax(predictions)])
        feature.progressBar.setValue(90)

class HeartSound(QMainWindow):
    def __init__(self):
        super(HeartSound, self).__init__()
        loadUi("ui_file/heartsound.ui", self)
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
        self.action_2.triggered.connect(self.onFileOpen)  ##菜单栏的action打开文件
        self.action_3.triggered.connect(self.close)  # 菜单栏的退出action
        self.play.clicked.connect(self.palyMusic)
        self.analysis.clicked.connect(self.Analyse_btn_start)
        self.pushButton.clicked.connect(self.volumeDown)
        self.pushButton_2.clicked.connect(self.volumeUp)
        #self.pushButton_3.clicked.connect(self.openmp3file)
        #self.pushButton_4.clicked.connect(self.mp32wav)
        self.pushButton_5.clicked.connect(self.onFileOpen)

        # Show The App
        self.show()


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

    def openmp3file(self):
        self.pathmp3, _ = QFileDialog.getOpenFileName(self, '打开文件', '', '音乐文件 (*.mp3)')
        msg = QMessageBox()
        msg.setWindowTitle("提示：")
        msg.setText("成功打开文件!")
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_()
        self.label_4.setText("当前文件名为:  " + os.path.basename(self.pathmp3))
        self.src = self.pathmp3
        self.dst = self.src.replace(".mp3", ".wav")
        print(self.src, type(self.src), self.dst, type(self.dst))

    def mp32wav(self):
        src = self.pathmp3
        dst = src.replace(".mp3", ".wav")
        # convert wav to mp3
        sound = AudioSegment.from_mp3(src)
        sound.export(dst , format="wav")
        msg = QMessageBox()
        msg.setWindowTitle("提示：")
        msg.setText("格式改变成功!")
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_()

    def Analyse_btn_start(self):##这里对应的是打开文件，并点击按钮
        try:
            if self.path:##要必须在打开文件之后才允许进行处理
                self.textBrowser.append(str(time.strftime("%Y %m %d %H:%M:%S", time.localtime())) )
                self.textBrowser.append("当前文件名 :"+str(os.path.basename(self.path)))
                self.progressBar.setValue(0)  ##每次允许处理时进度条归0
                self.Process.Audio_TimeDomain(self)  ##把实例传入进去
                self.Process.Audio_FrequencyDomain(self)
                self.Process.Audio_MFCCs(self)
                self.Process.Model_Apply(self)
                self.progressBar.setValue(100)
                self.textBrowser.append("分析成功!")


        except Exception as e:
            print(e)
            self.textBrowser.setText("There are some errors occuring when programme trying to open file")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeartSound()
    window.show()
    sys.exit(app.exec())