<template>
  <header class="app-header">
    <h1>Цифровой наставник в геологии</h1>
  </header>
  <div class="app-container">
    <!-- Каталог файлов (Левое меню) -->
    <div class="file-catalog">
      <h3>Каталог файлов</h3>
      <ul>
      <li v-for="(file, index) in uploadedFiles" :key="index">
        {{ file.name }}
        <button @click="selectFileFromCatalog(file)">Выбрать</button>
        <button @click="deleteFile(file)">Удалить</button>
      </li>
      </ul>
      <button @click="triggerCatalogFileInput">Загрузить</button>
      <input type="file" ref="catalogFileInput" @change="onFilesUpload" multiple style="display: none;" />
    </div>
    <!-- Диалоговое окно чата -->
    <div class="chat-container">
      <div class="chat-display" ref="chatDisplay">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message-wrapper"
          :class="message.sender === 'Вы' ? 'right' : 'left'"
        >
          <div class="message">
            <template v-if="message.isTyping">
              <span class="typing-indicator">
                Цифровой помощник печатает
                <span class="dot-one">.</span>
                <span class="dot-two">.</span>
                <span class="dot-three">.</span>
              </span>
            </template>
            <template v-else>
              {{ message.text }}
              <span v-if="message.hasFile" class="file-icon">📎 {{ message.file?.name }}</span>
              <button
                v-if="message.sender === 'Цифровой помощник' && !message.audioUrl && !message.isAudioLoading"
                class="audio-button"
                @click="generateAudio(message.text)"
              >
                🎤
              </button>
              <!-- Отображаем индикатор загрузки аудио -->
              <span v-if="message.isAudioLoading">Загрузка аудио...</span>
              <!-- Отображаем кнопку воспроизведения, если аудио готово -->
              <button
                v-if="message.audioUrl"
                class="play-button"
                @click="playAudio(message)"
              >
                🔊
              </button>
            </template>
          </div>
        </div>
      </div>

      <div class="input-container">
        <input type="file" ref="fileInput" @change="onFileSelected" style="display: none;" />
        <button class="file-attach-button" @click="triggerFileInput">📎</button>
        <div v-if="selectedFile" class="file-info">
          {{ selectedFile.name }}
          <button class="remove-file-button" @click="removeSelectedFile">❌</button>
        </div>
        <input class="chat-input" v-model="newMessage" placeholder="Введите сообщение..." />
        <button class="send-button" @click="sendMessage">✉️</button>
      </div>

      <div class="model-selector">
        <label for="model">Выберите модель: </label>
        <select v-model="selectedModel" id="model">
          <option v-for="model in models" :value="model.value" :key="model.value">{{ model.label }}</option>
        </select>
        <button @click="openAIRequest" class="openai-request-button">Запрос в OpenAI</button>
        <button @click="startInterview" class="interview-button">Провести интервью</button>
      </div>
    </div>
    <!-- Видео-контейнер справа -->
    <div class="video-container">
      <video
        :src="currentVideo"
        width="400"
        height="600"
        autoplay
        loop
        muted
      ></video>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      newMessage: '',
      messages: [],
      selectedFile: {
        file: null,
        catalogFileName: null,
        name: ''
      },
      files: [],
      uploadedFiles: [],
      selectedModel: 'llama3.1:7b',
      models: [
        {label: 'LLaMA 3.1 - 7B', value: 'llama3.1-7b'},
        {label: 'Qwen 2.5 - 7B', value: 'qwen2.5:7b'},
        {label: 'LLaMA 3.1 - 72B', value: 'llama3.1-72b'},
        {label: 'Qwen 2.5 - 72B', value: 'qwen2.5:72b'},
      ],
      currentVideo: '/videos/idle.mov',  // Начальное видео — ожидание
      videoSources: {
        idle: '/videos/untitled_2.mp4',
        thinking: '/videos/untitled_0.mp4',
        speaking: '/videos/untitled_3.mp4',
      },
      aiState: 'idle',  // Начальное состояние ИИ
    };
  },
  created() {
    this.fetchUploadedFiles();
    this.updateVideo();
  },
  methods: {
    async sendMessage() {
      const messageText = this.newMessage.trim();
      if (messageText || (this.selectedFile && (this.selectedFile.file || this.selectedFile.catalogFileName))) {
        const newMessage = { sender: 'Вы', text: messageText };
        if (this.selectedFile && (this.selectedFile.file || this.selectedFile.catalogFileName)) {
          newMessage.hasFile = true;
          newMessage.file = this.selectedFile;
        }
        this.messages.push(newMessage);
        this.newMessage = '';
        this.scrollToBottom();
        const typingMessage = { sender: 'Цифровой помощник', text: '', isTyping: true };
        this.messages.push(typingMessage);

        // Меняем состояние ИИ на "думает"
        this.aiState = 'thinking';
        this.updateVideo();

        try {
          const formData = new FormData();
          formData.append('message', messageText);
          formData.append('model', this.selectedModel);

          if (this.selectedFile.file) {
            formData.append('file', this.selectedFile.file);
          } else if (this.selectedFile.catalogFileName) {
            formData.append('catalogFileName', this.selectedFile.catalogFileName);
          }

          const response = await axios.post('http://localhost:8000/api/ollama_chat/', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            },
          });
          this.messages = this.messages.filter(msg => !msg.isTyping);
          this.scrollToBottom();
          typingMessage.isTyping = false;

          console.log('Ответ от сервера:', response.data); // Логируем данные ответа

          // Меняем состояние ИИ на "говорит"
          this.aiState = 'speaking';
          this.updateVideo();

          const assistantResponse = response.data.response || '';
          const message_id = response.data.message_id || null;

          const assistantMessage = {
            sender: 'Цифровой помощник',
          text: assistantResponse,
            id: message_id,
            isAudioLoading: false,
            audioUrl: null,
          };

          this.messages.push(assistantMessage);
          this.scrollToBottom();
          this.removeSelectedFile();

          setTimeout(() => {
            this.aiState = 'idle';
            this.updateVideo();
          }, 5000);
        } catch (error) {
          console.error('Ошибка при отправке сообщения:', error);
          this.aiState = 'idle';
          this.updateVideo();
        }
      }
    },
    triggerFileInput() {
  const fileInput = this.$refs.fileInput;
  if (fileInput) {
    fileInput.click();
  } else {
    console.error("fileInput reference not found.");
  }
},
triggerCatalogFileInput() {
  const catalogFileInput = this.$refs.catalogFileInput;
  if (catalogFileInput) {
    catalogFileInput.click();
  } else {
    console.error("catalogFileInput reference not found.");
  }
},
    onFileSelected(event) {
      const files = event.target.files;
      if (files.length > 0) {
        this.selectedFile = {
          file: files[0],
          catalogFileName: null,
          name: files[0].name,
        };
      }
    },
    removeSelectedFile() {
  this.selectedFile = {
    file: null,
    catalogFileName: null,
    name: ''
  };
},
    async fetchUploadedFiles() {
      try {
        const response = await axios.get('http://localhost:8000/api/files/');
        this.uploadedFiles = response.data.files;
      } catch (error) {
        console.error('Ошибка при загрузке файлов:', error);
      }
    },
    async onFilesUpload(event) {
      const files = event.target.files;
      if (files.length === 0) return;

      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }

      try {
        const response = await axios.post('http://localhost:8000/api/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.uploadedFiles.push(...response.data.files);
      } catch (error) {
        console.error('Ошибка при загрузке файлов:', error);
      }
    },
    selectFileFromCatalog(file) {
      this.selectedFile = {
        file: null,
        catalogFileName: file.name,
        name: file.name,
      };
    },
    async deleteFile(file) {
      try {
        await axios.post('http://localhost:8000/api/delete/', { fileName: file.name });
        this.uploadedFiles = this.uploadedFiles.filter(f => f.name !== file.name);
      } catch (error) {
        console.error('Ошибка при удалении файла:', error);
      }
    },
     scrollToBottom() {
  this.$nextTick(() => {
    const chatDisplay = this.$refs.chatDisplay;
    if (chatDisplay) {
      chatDisplay.scrollTop = chatDisplay.scrollHeight;
    } else {
      console.error("chatDisplay reference not found.");
    }
  });
},
    updateVideo() {
      this.currentVideo = this.videoSources[this.aiState];
    },
  },
  async generateAudio(messageText) {
      // Проверяем, не идет ли уже генерация аудио
      if (messageText.isAudioLoading) return;

      messageText.isAudioLoading = true;

      try {
        const response = await axios.post(`http://localhost:8000/api/generate_audio/`, {
          text: messageText, // Передаем текст сообщения
        });

        if (response.data.audio_url) {
          messageText.audioUrl = response.data.audio_url;
        } else {
          console.error('Аудио URL не найден в ответе сервера');
        }
      } catch (error) {
        console.error('Ошибка при генерации аудио:', error);
      } finally {
        messageText.isAudioLoading = false;
      }
    },

    playAudio(message) {
      if (message.audioUrl) {
        const audio = new Audio(message.audioUrl);
        audio.play();
      }
    },
};
</script>

<style scoped>

body {
  display: flex;
  justify-content: center; /* Горизонтальное центрирование */
  align-items: center;    /* Вертикальное центрирование */
  background-color: #f0f0f0; /* Фоновый цвет для всей страницы */
}
/* Шапка */
.app-header {
  background-color: #1867c0;
  color: white;
  text-align: center;
  padding: 20px;
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
}
.app-header h1 {
  margin: 0;
  font-size: 24px;
}
.app-container {
  display: flex;
  justify-content: space-between;
  height: 80vh;
  width: 90vw;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.file-catalog {
  width: 15vw; /* Ширина левого меню */
  background-color: #f8f8f8;
  padding: 10px;
  border-right: 1px solid #ccc;
  overflow-y: auto;
}

.file-catalog h3 {
  margin-top: 0;
}

ul {
  list-style: none;
  padding: 0;
}

.interview-button, .openai-request-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  margin: 10px;
  cursor: pointer;
  border-radius: 5px;
  width: 10%;
}

.interview-button:hover, .openai-request-button:hover {
  background-color: #0056b3;
}

li {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}

.file-catalog ul {
  list-style: none;
  padding: 0;
}

.file-catalog li {
  padding: 8px;
  margin-bottom: 5px;
  background-color: #e0e0e0;
  border-radius: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-catalog li:hover {
  background-color: #1867c0;
}

.file-catalog button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 5px 10px;
  cursor: pointer;
}

.file-catalog button:hover {
  background-color: #0056b3;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 10px;
  background-color: #f1f1f1;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  padding: 15px;
}

.chat-display {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  border-radius: 10px;
  background-color: white;
  display: flex;
  flex-direction: column;
}

.video-container {
  width: 15vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f8f8;
  border-left: 1px solid #ccc;
}

.video-container video {
  max-width: 100%;
  max-height: 100%;
  border-radius: 10px;
}

.message-wrapper {
  display: flex;
  margin-bottom: 10px;
}

.message-wrapper.right {
  justify-content: flex-end;
}

.message-wrapper.left {
  justify-content: flex-start;
}

.message {
  background-color: #e0e0e0;
  padding: 10px;
  border-radius: 10px;
  max-width: 70%;
  position: relative;
}

.file-icon {
  margin-left: 10px;
  font-size: 14px;
  color: #1867c0;
}

.input-container {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: white;
  border-top: 1px solid #ccc;
  border-radius: 0 0 10px 10px;
  gap: 10px;
  flex-wrap: wrap;
}

.chat-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 10px;
}

.file-attach-button,
.send-button {
  background-color: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.file-attach-button {
  flex: 0 0 40px;
}

.send-button {
  flex: 0 0 40px;
  color: #1867c0;
}

.file-info {
  margin-left: 10px;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.remove-file-button {
  margin-left: 5px;
  color: red;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .file-catalog {
    width: 25vw;
  }
}

@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }

  .file-catalog {
    width: 100%;
    max-height: 30vh;
    border-right: none;
    border-bottom: 1px solid #ccc;
  }

  .chat-container {
    width: 100%;
    margin: 0;
    border-radius: 0;
    box-shadow: none;
  }

  .remove-file-button {
    margin-left: 5px;
    color: red;
    cursor: pointer;
  }
.interview-button:hover {
  background-color: #0056b3;
}
.interview-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  margin-top: 10px;
  cursor: pointer;
  border-radius: 5px;
  display: block; /* Кнопка в отдельной строке под видео */
  width: 10%; /* Растягиваем кнопку по всей ширине контейнера */
}

.openai-request-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 5px 10px; /* Сужаем кнопку */
  cursor: pointer;
  border-radius: 5px;
  margin-left: 10px; /* Отступ для красоты */
}

.openai-request-button:hover {
  background-color: #0056b3;
}
  .model-selector {
    display: flex;
    align-items: center;
    margin-right: 10px;
  }

  .model-selector label {
    margin-right: 5px;
  }

  .model-selector select {
    padding: 5px;
    border-radius: 5px;
    border: 1px solid #ccc;
  }

  .typing-indicator {
    display: inline-block;
  }

  .typing-indicator .dot-one,
  .typing-indicator .dot-two,
  .typing-indicator .dot-three {
    display: inline-block;
    animation: blink 1.4s infinite both;
  }

  .typing-indicator .dot-one {
    animation-delay: 0s;
  }

  .typing-indicator .dot-two {
    animation-delay: 0.2s;
  }

  .typing-indicator .dot-three {
    animation-delay: 0.4s;
  }

  @keyframes blink {
    0% {
      opacity: 0.2;
    }
    20% {
      opacity: 1;
    }
    100% {
      opacity: 0.2;
    }
  }
}
.audio-button {
  width: 10%;
  display: inline-block;
}
</style>