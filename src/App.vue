<template>
  <div class="container">
    <header>
      <h1>Варианты квизов — выбери подходящий</h1>
      <p class="subtitle">Каждый вариант выглядит именно так, как если бы его сделал школьник. Попробуй
        взаимодействовать!</p>
    </header>

    <div class="options-grid" :class="{ 'has-active': activeCard !== null, 'is-expanding': expandingCard !== null }">
      <!-- Вариант 1: Консольный -->
      <div 
        class="option-card" 
        :class="{ 
          flipped: cards.console.flipped,
          active: activeCard === 'console'
        }"
        v-show="activeCard === null || activeCard === 'console'">
        <div class="flip-icon" @click="flipCard('console')">🔍</div>
        <div class="card-flip-container">
          <div class="card-front">
            <div class="card-header">
              <h2>Консольный квиз</h2>
              <p>Текст в чёрном окне — как настоящий программист!</p>
            </div>
            <div class="preview-area">
              <div class="console-preview">
                <div class="console-line">
                  <span class="console-prompt">&gt;</span>
                  <span class="console-text">КВИЗ ПО ГЕОГРАФИИ!!!</span>
                </div>
                <div class="console-line">
                  <span class="console-prompt">&gt;</span>
                  <span class="console-text">Столица Франции?</span>
                </div>
                <div class="console-line">
                  <span class="console-prompt">&gt;</span>
                  <span class="console-text">Выбери ответ:</span>
                </div>
                <div class="console-options">
                  <div 
                    v-for="(option, index) in quizData.console.options" 
                    :key="index"
                    class="console-option">
                    <span class="console-prompt">&gt;</span>
                    <span class="console-text">{{ index + 1 }}. {{ option.text }}</span>
                  </div>
                </div>
                <div class="console-line">
                  <span class="console-prompt">&gt;</span>
                  <input 
                    type="text" 
                    class="console-input" 
                    v-model="quizData.console.selectedAnswer"
                    @keypress.enter="checkConsole"
                    :disabled="quizData.console.checked"
                    placeholder="Введи цифру (1-4)...">
                </div>
                <div class="console-line" v-if="quizData.console.result">
                  <span class="console-prompt">&gt;</span>
                  <span :class="quizData.console.resultType === 'success' ? 'console-output' : 'console-error'">
                    {{ quizData.console.result }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div class="card-back">
            <div class="code-header">
              <h3>Python код — Консольный квиз</h3>
            </div>
            <div class="code-content">{{ codeSnippets.console }}</div>
          </div>
        </div>
      </div>

      <!-- Вариант 2: Tkinter -->
      <div 
        class="option-card" 
        :class="{ 
          flipped: cards.tkinter.flipped,
          active: activeCard === 'tkinter'
        }"
        v-show="activeCard === null || activeCard === 'tkinter'">
        <div class="flip-icon" @click="flipCard('tkinter')">🔍</div>
        <div class="card-flip-container">
          <div class="card-front">
            <div class="card-header">
              <h2>Оконный квиз (Tkinter)</h2>
              <p>Программа с кнопочками — как в старых Windows! С картинкой и "Далее"!</p>
            </div>
            <div class="preview-area">
              <div class="tkinter-preview">
                <div class="tkinter-window">
                  <div class="tkinter-title">МОЙ КВИЗ ПО ИСТОРИИ!!!</div>
                  <template v-if="quizData.tkinter.step === 1">
                    <div class="tkinter-label">Кто открыл Америку?</div>
                    <div class="tkinter-options">
                      <label 
                        v-for="(option, index) in quizData.tkinter.options1" 
                        :key="index"
                        class="tkinter-radio-label"
                        :class="{ disabled: quizData.tkinter.checked1 }">
                        <input 
                          type="radio" 
                          name="tkinter-answer1"
                          :value="option.value"
                          v-model="quizData.tkinter.selectedAnswer1"
                          :disabled="quizData.tkinter.checked1"
                          class="tkinter-radio">
                        <span class="tkinter-radio-text">{{ option.text }}</span>
                      </label>
                    </div>
                    <div class="tkinter-button" @click="checkTkinter">ПРОВЕРИТЬ ОТВЕТ!!</div>
                    <div class="tkinter-image" v-show="quizData.tkinter.showImage1">
                      <img :src="quizData.tkinter.image1Url" alt="Результат">
                    </div>
                    <div class="tkinter-next-button" v-show="quizData.tkinter.showNext1" @click="nextTkinter">
                      ДАЛЕЕ ➡️
                    </div>
                    <div class="tkinter-result" v-show="quizData.tkinter.result1">
                      {{ quizData.tkinter.result1 }}
                    </div>
                  </template>
                  <template v-else-if="quizData.tkinter.step === 2">
                    <div class="tkinter-label">Сколько было подвигов у Геракла?</div>
                    <div class="tkinter-options">
                      <label 
                        v-for="(option, index) in quizData.tkinter.options2" 
                        :key="index"
                        class="tkinter-radio-label"
                        :class="{ disabled: quizData.tkinter.checked2 }">
                        <input 
                          type="radio" 
                          name="tkinter-answer2"
                          :value="option.value"
                          v-model="quizData.tkinter.selectedAnswer2"
                          :disabled="quizData.tkinter.checked2"
                          class="tkinter-radio">
                        <span class="tkinter-radio-text">{{ option.text }}</span>
                      </label>
                    </div>
                    <div class="tkinter-button" @click="checkTkinter2">ПРОВЕРИТЬ ОТВЕТ!!</div>
                    <div class="tkinter-image" v-show="quizData.tkinter.showImage2">
                      <img :src="quizData.tkinter.image2Url" alt="Результат">
                    </div>
                    <div class="tkinter-next-button" v-show="quizData.tkinter.showNext2" @click="finishTkinter">
                      ЗАВЕРШИТЬ
                    </div>
                    <div class="tkinter-result" v-show="quizData.tkinter.result2">
                      {{ quizData.tkinter.result2 }}
                    </div>
                  </template>
                  <template v-else>
                    <div style="text-align: center; margin: 20px 0;">
                      <img src="/images/quiz-completion.jpg" alt="Поздравление" style="max-width: 400px; width: 100%; height: auto; border: 3px solid #27ae60; border-radius: 12px; margin: 0 auto 20px; display: block;">
                      <div style="font-size: 1.2rem; font-weight: bold; color: #27ae60;">ПОЗДРАВЛЯЮ! ТЫ ПРОШЁЛ ВЕСЬ КВИЗ!</div>
                      <div style="margin-top: 15px; color: #2c3e50;">Ты настоящий знаток истории! 🏆</div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </div>
          <div class="card-back">
            <div class="code-header">
              <h3>Python код — Tkinter квиз</h3>
            </div>
            <div class="code-content">{{ codeSnippets.tkinter }}</div>
          </div>
        </div>
      </div>

      <!-- Вариант 3: Веб-форма -->
      <div 
        class="option-card" 
        :class="{ 
          flipped: cards.web.flipped,
          active: activeCard === 'web'
        }"
        v-show="activeCard === null || activeCard === 'web'">
        <div class="flip-icon" @click="flipCard('web')">🔍</div>
        <div class="card-flip-container">
          <div class="card-front">
            <div class="card-header">
              <h2>Веб-квиз</h2>
              <p>Красивая форма в браузере — как настоящий сайт!</p>
            </div>
            <div class="preview-area">
              <div class="web-preview">
                <div class="web-title">КВИЗ ДЛЯ УМНИКОВ! 🧠</div>
                <template v-if="quizData.web.step === 1">
                  <div class="web-question">Сколько будет 7 × 8?</div>
                  <div class="web-options">
                    <div 
                      v-for="(option, index) in quizData.web.options" 
                      :key="index"
                      class="web-option"
                      :class="{ 
                        selected: quizData.web.selectedAnswer === option.value,
                        disabled: quizData.web.checked
                      }"
                      @click="!quizData.web.checked && (quizData.web.selectedAnswer = option.value)">
                      {{ option.text }}
                    </div>
                  </div>
                  <button class="web-button" @click="checkWeb">ПРОВЕРИТЬ!</button>
                  <div class="web-image" v-show="quizData.web.showImage">
                    <img :src="quizData.web.imageUrl" alt="Результат">
                  </div>
                  <div class="web-result" :class="quizData.web.resultType" v-show="quizData.web.result">
                    {{ quizData.web.result }}
                  </div>
                  <button class="web-next-button" v-show="quizData.web.showNext" @click="nextWeb">
                    ПРОДОЛЖИТЬ ➡️
                  </button>
                </template>
                <template v-else-if="quizData.web.step === 2">
                  <div class="web-question">Сколько будет 15 + 23?</div>
                  <div class="web-options">
                    <div 
                      v-for="(option, index) in quizData.web.options2" 
                      :key="index"
                      class="web-option"
                      :class="{ 
                        selected: quizData.web.selectedAnswer2 === option.value,
                        disabled: quizData.web.checked2
                      }"
                      @click="!quizData.web.checked2 && (quizData.web.selectedAnswer2 = option.value)">
                      {{ option.text }}
                    </div>
                  </div>
                  <button class="web-button" @click="checkWeb2">ПРОВЕРИТЬ!</button>
                  <div class="web-image" v-show="quizData.web.showImage2">
                    <img :src="quizData.web.imageUrl2" alt="Результат">
                  </div>
                  <div class="web-result" :class="quizData.web.resultType2" v-show="quizData.web.result2">
                    {{ quizData.web.result2 }}
                  </div>
                  <button class="web-finish-button" v-show="quizData.web.showFinish" @click="finishWeb">
                    ЗАВЕРШИТЬ
                  </button>
                </template>
                <template v-else>
                  <div style="text-align: center; margin: 20px 0;">
                    <img src="/images/quiz-completion.jpg" alt="Поздравление" style="max-width: 400px; width: 100%; height: auto; border: 3px solid #3182ce; border-radius: 12px; margin: 0 auto 20px; display: block;">
                    <div style="font-size: 1.2rem; font-weight: bold; color: #3182ce;">ПОЗДРАВЛЯЮ! ТЫ ПРОШЁЛ ВЕСЬ КВИЗ!</div>
                    <div style="margin-top: 15px; color: #2d3748;">Ты настоящий умник! 🏆</div>
                  </div>
                </template>
              </div>
            </div>
          </div>
          <div class="card-back">
            <div class="code-header">
              <h3>Python код — Веб-квиз (Flask)</h3>
            </div>
            <div class="code-content">{{ codeSnippets.web }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="note-section">
      <h2>Какой выбрать?</h2>
      <div class="note-content">
        <p>• <span class="highlight-text">Консольный</span> — самый простой для школьника, выглядит "сыро" и
          по-настоящему</p>
        <p>• <span class="highlight-text">Tkinter</span> — как старая Windows-программа, с картинкой и кнопкой
          "Далее"! Совсем как школьная поделка.</p>
        <p>• <span class="highlight-text">Веб-квиз</span> — выглядит современно, можно показать друзьям как
          "сайт"</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      activeCard: null, // null means no card is active, 'console' | 'tkinter' | 'web' when one is active
      expandingCard: null, // Card that is currently expanding
      cards: {
        console: { flipped: false },
        tkinter: { flipped: false },
        web: { flipped: false }
      },
      quizData: {
        console: {
          selectedAnswer: '',
          options: [
            { text: 'Париж', value: 'париж' },
            { text: 'Лондон', value: 'лондон' },
            { text: 'Берлин', value: 'берлин' },
            { text: 'Мадрид', value: 'мадрид' }
          ],
          result: '',
          resultType: '',
          checked: false
        },
        tkinter: {
          step: 1,
          selectedAnswer1: null,
          options1: [
            { text: 'Колумб', value: 'колумб' },
            { text: 'Васко да Гама', value: 'васко да гама' },
            { text: 'Магеллан', value: 'магеллан' },
            { text: 'Кук', value: 'кук' }
          ],
          selectedAnswer2: null,
          options2: [
            { text: '10', value: '10' },
            { text: '12', value: '12' },
            { text: '14', value: '14' },
            { text: '15', value: '15' }
          ],
          result1: '',
          result2: '',
          showImage1: false,
          image1Url: '',
          showNext1: false,
          showImage2: false,
          image2Url: '',
          showNext2: false,
          checked1: false,
          checked2: false
        },
        web: {
          step: 1,
          selectedAnswer: null,
          options: [
            { text: '54', value: '54' },
            { text: '56', value: '56' },
            { text: '58', value: '58' },
            { text: '60', value: '60' }
          ],
          selectedAnswer2: null,
          options2: [
            { text: '36', value: '36' },
            { text: '38', value: '38' },
            { text: '40', value: '40' },
            { text: '42', value: '42' }
          ],
          result: '',
          resultType: '',
          result2: '',
          resultType2: '',
          showImage: false,
          imageUrl: '',
          showImage2: false,
          imageUrl2: '',
          showNext: false,
          showFinish: false,
          checked: false,
          checked2: false
        }
      },
      catImages: {
        success: '/images/cat-success.jpg',
        error: '/images/cat-error.jpg'
      },
      codeSnippets: {
        console: `print("КВИЗ ПО ГЕОГРАФИИ!!!")
print("Столица Франции?")
print("Выбери ответ:")
print("1. Париж")
print("2. Лондон")
print("3. Берлин")
print("4. Мадрид")

choice = input("Твой выбор (1-4): ")

if choice.strip() == "1":
    print("ПРАВИЛЬНО! МОЛОДЕЦ! 🎉")
else:
    print("НЕПРАВИЛЬНО! В СЛЕДУЮЩИЙ РАЗ ПОВЕЗЁТ!")

print("\\n--- Конец квиза ---")`,
        tkinter: `import tkinter as tk
from tkinter import messagebox

selected_answer = tk.StringVar()

def check_answer():
    answer = selected_answer.get()
    if not answer:
        result_label.config(text="Выбери ответ!", bg="#fed7d7")
        result_label.pack()
        return
    
    if answer == "колумб":
        result_label.config(text="ПРАВИЛЬНО! ТЫ МОЛОДЕЦ! 🍪", 
                          bg="#c6f6d5", fg="#2f855a")
        image_label.pack()
        next_button.pack()
    else:
        result_label.config(text="НЕПРАВИЛЬНО! В СЛЕДУЮЩИЙ РАЗ ПОВЕЗЁТ!", 
                          bg="#fed7d7", fg="#e53e3e")
        image_label.pack_forget()
        next_button.pack_forget()
    result_label.pack()

def next_question():
    # Переход к следующему вопросу
    pass

root = tk.Tk()
root.title("МОЙ КВИЗ ПО ИСТОРИИ!!!")
root.geometry("400x400")

title_label = tk.Label(root, text="МОЙ КВИЗ ПО ИСТОРИИ!!!", 
                       font=("Arial", 14, "bold"))
title_label.pack(pady=10)

question_label = tk.Label(root, text="Кто открыл Америку?")
question_label.pack(pady=5)

options = [
    ("Колумб", "колумб"),
    ("Васко да Гама", "васко да гама"),
    ("Магеллан", "магеллан"),
    ("Кук", "кук")
]

for text, value in options:
    radio = tk.Radiobutton(root, text=text, variable=selected_answer,
                          value=value, bg="#f0f0f0", font=("Arial", 10))
    radio.pack(anchor="w", padx=20, pady=3)

check_button = tk.Button(root, text="ПРОВЕРИТЬ ОТВЕТ!!", 
                         command=check_answer, bg="#dcdcdc")
check_button.pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 12))
image_label = tk.Label(root, text="🏆", font=("Arial", 50))
next_button = tk.Button(root, text="ДАЛЕЕ ➡️", command=next_question,
                        bg="#27ae60", fg="white")

root.mainloop()`,
        web: `from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = '''
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;КВИЗ ДЛЯ УМНИКОВ! 🧠&lt;/title&gt;
    &lt;style&gt;
        body { font-family: Arial; text-align: center; padding: 50px; }
        .option { padding: 10px; margin: 10px; background: #e2e8f0; 
                 cursor: pointer; border: 2px solid transparent; }
        .option:hover { background: #cbd5e0; }
        .option.selected { background: #90cdf4; border-color: #3182ce; }
        button { padding: 10px 20px; background: #3182ce; 
                color: white; border: none; cursor: pointer; }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;КВИЗ ДЛЯ УМНИКОВ! 🧠&lt;/h1&gt;
    &lt;p&gt;Сколько будет 7 × 8?&lt;/p&gt;
    &lt;form method="POST"&gt;
        &lt;div class="option" onclick="selectOption('54')"&gt;54&lt;/div&gt;
        &lt;div class="option" onclick="selectOption('56')"&gt;56&lt;/div&gt;
        &lt;div class="option" onclick="selectOption('58')"&gt;58&lt;/div&gt;
        &lt;div class="option" onclick="selectOption('60')"&gt;60&lt;/div&gt;
        &lt;input type="hidden" name="answer" id="answer"&gt;
        &lt;br&gt;
        &lt;button type="submit"&gt;ПРОВЕРИТЬ!&lt;/button&gt;
    &lt;/form&gt;
    &lt;div id="result"&gt;{{ result }}&lt;/div&gt;
    &lt;script&gt;
        function selectOption(value) {
            document.getElementById('answer').value = value;
            document.querySelectorAll('.option').forEach(el =&gt; 
                el.classList.remove('selected'));
            event.target.classList.add('selected');
        }
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
'''

@app.route('/', methods=['GET', 'POST'])
def quiz():
    result = ""
    if request.method == 'POST':
        answer = request.form.get('answer', '').strip()
        if answer == "56":
            result = "ПРАВИЛЬНО! ТЫ МОЛОДЕЦ! ★☆★"
        else:
            result = "НЕПРАВИЛЬНО! В СЛЕДУЮЩИЙ РАЗ ПОВЕЗЁТ!"
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True)`
      }
    }
  },
  methods: {
    flipCard(cardType) {
      const wasFlipped = this.cards[cardType].flipped
      
      // If card was flipped and we're flipping it back, collapse first then flip
      if (wasFlipped) {
        // First collapse (remove active state) - animation 0.4s
        this.activeCard = null
        this.expandingCard = null
        
        // Then flip back after collapse animation completes
        setTimeout(() => {
          this.cards[cardType].flipped = false
        }, 400) // Wait for collapse animation (0.4s)
      } else {
        // Close all other cards first
        Object.keys(this.cards).forEach(key => {
          if (key !== cardType) {
            this.cards[key].flipped = false
          }
        })
        this.activeCard = null
        this.expandingCard = null
        
        // First flip the card - animation 0.6s
        this.cards[cardType].flipped = true
        
        // Then expand after flip animation completes (0.6s)
        setTimeout(() => {
          this.activeCard = cardType
          this.expandingCard = cardType
          
          // Remove expanding flag after expansion completes (0.4s)
          setTimeout(() => {
            this.expandingCard = null
          }, 400)
        }, 600) // Wait for flip animation to complete (0.6s)
      }
    },
    checkConsole() {
      if (this.quizData.console.checked) return
      
      const answer = this.quizData.console.selectedAnswer.trim()
      if (!answer) {
        this.quizData.console.result = 'Введи цифру!'
        this.quizData.console.resultType = 'error'
        return
      }
      // Check if answer is "1" (first option - Париж)
      if (answer === '1') {
        this.quizData.console.result = 'ПРАВИЛЬНО! МОЛОДЕЦ! 🎉'
        this.quizData.console.resultType = 'success'
      } else {
        this.quizData.console.result = 'НЕПРАВИЛЬНО! В СЛЕДУЮЩИЙ РАЗ ПОВЕЗЁТ!'
        this.quizData.console.resultType = 'error'
      }
      this.quizData.console.checked = true
    },
    checkTkinter() {
      if (this.quizData.tkinter.checked1) return
      
      if (!this.quizData.tkinter.selectedAnswer1) {
        this.quizData.tkinter.result1 = 'Выбери ответ!'
        return
      }
      if (this.quizData.tkinter.selectedAnswer1 === 'колумб') {
        this.quizData.tkinter.result1 = 'ПРАВИЛЬНО! ТЫ МОЛОДЕЦ! 🍪'
        this.quizData.tkinter.showImage1 = true
        this.quizData.tkinter.image1Url = this.catImages.success
      } else {
        this.quizData.tkinter.result1 = 'НЕПРАВИЛЬНО! В СЛЕДУЮЩИЙ РАЗ ПОВЕЗЁТ!'
        this.quizData.tkinter.showImage1 = true
        this.quizData.tkinter.image1Url = this.catImages.error
      }
      this.quizData.tkinter.showNext1 = true
      this.quizData.tkinter.checked1 = true
    },
    nextTkinter() {
      this.quizData.tkinter.step = 2
      this.quizData.tkinter.selectedAnswer1 = null
      this.quizData.tkinter.result1 = ''
      this.quizData.tkinter.showImage1 = false
      this.quizData.tkinter.image1Url = ''
      this.quizData.tkinter.showNext1 = false
      this.quizData.tkinter.checked1 = false
    },
    checkTkinter2() {
      if (this.quizData.tkinter.checked2) return
      
      if (!this.quizData.tkinter.selectedAnswer2) {
        this.quizData.tkinter.result2 = 'Выбери ответ!'
        return
      }
      if (this.quizData.tkinter.selectedAnswer2 === '12') {
        this.quizData.tkinter.result2 = 'ПРАВИЛЬНО! ТЫ УМНИЦА! 🌟'
        this.quizData.tkinter.showImage2 = true
        this.quizData.tkinter.image2Url = this.catImages.success
      } else {
        this.quizData.tkinter.result2 = 'НЕПРАВИЛЬНО! В СЛЕДУЮЩИЙ РАЗ ПОВЕЗЁТ!'
        this.quizData.tkinter.showImage2 = true
        this.quizData.tkinter.image2Url = this.catImages.error
      }
      this.quizData.tkinter.showNext2 = true
      this.quizData.tkinter.checked2 = true
    },
    finishTkinter() {
      this.quizData.tkinter.step = 3
    },
    checkWeb() {
      if (this.quizData.web.checked) return
      
      if (!this.quizData.web.selectedAnswer) {
        this.quizData.web.result = 'Выбери ответ!'
        this.quizData.web.resultType = 'error'
        return
      }
      if (this.quizData.web.selectedAnswer === '56') {
        this.quizData.web.result = 'ПРАВИЛЬНО! ТЫ МОЛОДЕЦ! ★☆★'
        this.quizData.web.resultType = 'success'
        this.quizData.web.showImage = true
        this.quizData.web.imageUrl = this.catImages.success
      } else {
        this.quizData.web.result = 'НЕПРАВИЛЬНО! В СЛЕДУЮЩИЙ РАЗ ПОВЕЗЁТ!'
        this.quizData.web.resultType = 'error'
        this.quizData.web.showImage = true
        this.quizData.web.imageUrl = this.catImages.error
      }
      this.quizData.web.showNext = true
      this.quizData.web.checked = true
    },
    nextWeb() {
      this.quizData.web.step = 2
      this.quizData.web.selectedAnswer = null
      this.quizData.web.result = ''
      this.quizData.web.showImage = false
      this.quizData.web.imageUrl = ''
      this.quizData.web.showNext = false
      this.quizData.web.checked = false
    },
    checkWeb2() {
      if (this.quizData.web.checked2) return
      
      if (!this.quizData.web.selectedAnswer2) {
        this.quizData.web.result2 = 'Выбери ответ!'
        this.quizData.web.resultType2 = 'error'
        return
      }
      if (this.quizData.web.selectedAnswer2 === '38') {
        this.quizData.web.result2 = 'ПРАВИЛЬНО! ТЫ МОЛОДЕЦ! ★☆★'
        this.quizData.web.resultType2 = 'success'
        this.quizData.web.showImage2 = true
        this.quizData.web.imageUrl2 = this.catImages.success
      } else {
        this.quizData.web.result2 = 'НЕПРАВИЛЬНО! В СЛЕДУЮЩИЙ РАЗ ПОВЕЗЁТ!'
        this.quizData.web.resultType2 = 'error'
        this.quizData.web.showImage2 = true
        this.quizData.web.imageUrl2 = this.catImages.error
      }
      this.quizData.web.showFinish = true
      this.quizData.web.checked2 = true
    },
    finishWeb() {
      this.quizData.web.step = 3
    }
  }
}
</script>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body {
    background: linear-gradient(135deg, #f0f4f8 0%, #e6e9f0 100%);
    padding: 20px;
    color: #2d3238;
    line-height: 1.6;
}

.container {
    max-width: 1600px;
    margin: 0 auto;
}

header {
    text-align: center;
    padding: 40px 0 50px;
}

h1 {
    font-size: 2.8rem;
    color: #1a365d;
    margin-bottom: 16px;
    font-weight: 800;
}

.subtitle {
    font-size: 1.25rem;
    color: #4a5568;
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.7;
}

.options-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 35px;
    margin-bottom: 60px;
}

.options-grid.has-active {
    gap: 0;
    transition: gap 0.4s ease 0.65s;
}

.options-grid:not(.has-active) {
    transition: gap 0.4s ease;
}

.options-grid.has-active .option-card:not(.active) {
    opacity: 0;
    pointer-events: none;
    flex: 0 0 0;
    width: 0;
    overflow: hidden;
    min-width: 0;
    transition: opacity 0.3s ease, flex 0.4s ease 0.65s, width 0.4s ease 0.65s, min-width 0.4s ease 0.65s;
}

.options-grid:not(.has-active) .option-card {
    opacity: 1;
    pointer-events: all;
    flex: 1 1 350px;
    min-width: 350px;
    width: auto;
    transition: opacity 0.3s ease 0.4s, flex 0.4s ease, width 0.4s ease, min-width 0.4s ease;
}

.option-card {
    background: transparent;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    position: relative;
    height: 950px;
    perspective: 1000px;
    transition: transform 0.3s ease, box-shadow 0.3s ease, height 0.4s ease, flex 0.4s ease, width 0.4s ease, opacity 0.3s ease, min-width 0.4s ease;
}

.option-card.active {
    height: 1050px;
    flex: 1 1 100%;
    width: 100%;
    min-width: 100%;
    transition: transform 0.3s ease, box-shadow 0.3s ease, height 0.4s ease 0.65s, flex 0.4s ease 0.65s, width 0.4s ease 0.65s, min-width 0.4s ease 0.65s, opacity 0.3s ease;
}

.options-grid.has-active .option-card.active {
    margin: 0 auto;
}

.option-card:hover:not(.flipped) {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
}

.card-flip-container {
    position: relative;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.option-card.flipped .card-flip-container {
    transform: rotateY(180deg);
}

.card-front,
.card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    border-radius: 18px;
    overflow-y: auto;
    overflow-x: hidden;
}

.card-front {
    background: white;
    transform: rotateY(0deg);
}

.card-back {
    transform: rotateY(180deg);
    background: white;
    border-radius: 18px;
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
}

.flip-icon {
    position: absolute;
    top: 15px;
    left: 15px;
    z-index: 10;
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.flip-icon:hover {
    background: rgba(255, 255, 255, 1);
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.code-header {
    background: #1e1e1e;
    color: white;
    padding: 20px 25px;
    text-align: center;
    border-bottom: 2px solid #333;
}

.code-header h3 {
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0;
}

.code-content {
    flex: 1;
    overflow-y: auto;
    padding: 25px;
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre;
}

.code-content::-webkit-scrollbar {
    width: 8px;
}

.code-content::-webkit-scrollbar-track {
    background: #2d2d2d;
}

.code-content::-webkit-scrollbar-thumb {
    background: #555;
    border-radius: 4px;
}

.code-content::-webkit-scrollbar-thumb:hover {
    background: #666;
}

.card-header {
    padding: 25px;
    background: #2c5282;
    color: white;
    text-align: center;
}

.card-header h2 {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.card-header p {
    opacity: 0.9;
    font-size: 1rem;
}

.preview-area {
    padding: 25px;
    min-height: 600px;
    display: flex;
    flex-direction: column;
}

/* Console style */
.console-preview {
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Courier New', monospace;
    border-radius: 12px;
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.console-line {
    display: flex;
    align-items: flex-start;
    gap: 10px;
}

.console-prompt {
    color: #4ec9b0;
    min-width: 20px;
}

.console-text {
    color: #d4d4d4;
}

.console-input {
    color: #d4d4d4;
    outline: none;
    background: transparent;
    border: none;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    width: 120px;
    border-bottom: 1px solid #569cd6;
}

.console-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    border-bottom-color: #666;
}

.console-output {
    color: #b5cea8;
}

.console-error {
    color: #f48771;
}

.console-options {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 10px 0;
}

.console-option {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
}

/* Tkinter style */
.tkinter-preview {
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 12px;
    padding: 20px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.tkinter-window {
    background: white;
    border: 2px solid #a0a0a0;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    min-height: 500px;
    display: flex;
    flex-direction: column;
}

.tkinter-title {
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 15px;
    font-size: 1.1rem;
    text-align: center;
}

.tkinter-label {
    margin-bottom: 12px;
    color: #2c3e50;
    font-size: 0.95rem;
    text-align: center;
}

.tkinter-input {
    width: 100%;
    padding: 8px 12px;
    border: 2px solid #a0a0a0;
    border-radius: 4px;
    margin-bottom: 15px;
    background: white;
    text-align: center;
}

.tkinter-button {
    background: #dcdcdc;
    color: #000;
    border: 2px solid #a0a0a0;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    text-align: center;
    width: fit-content;
    margin: 0 auto;
}

.tkinter-result {
    margin-top: 15px;
    padding: 10px;
    background: #e8f4fd;
    border-radius: 6px;
    font-size: 0.95rem;
    color: #2980b9;
    text-align: center;
}

.tkinter-image {
    text-align: center;
    margin: 15px 0;
}

.tkinter-image img {
    max-width: 200px;
    max-height: 200px;
    width: auto;
    height: auto;
    object-fit: contain;
    border: 2px solid #2980b9;
    border-radius: 8px;
}

.tkinter-next-button {
    background: #27ae60;
    color: white;
    border: 2px solid #219653;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    text-align: center;
    width: fit-content;
    margin: 10px auto 0;
}

.tkinter-options {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 15px;
}

.tkinter-radio-label {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px 12px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    border-radius: 4px;
    transition: all 0.2s ease;
}

.tkinter-radio-label:hover {
    background: #e0e0e0;
}

.tkinter-radio {
    margin-right: 10px;
    cursor: pointer;
    width: 18px;
    height: 18px;
}

.tkinter-radio-text {
    font-size: 0.95rem;
    color: #2c3e50;
    user-select: none;
}

.tkinter-radio-label.disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
}

.tkinter-radio:disabled {
    cursor: not-allowed;
}

/* Web form style */
.web-preview {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 25px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
    box-shadow: inset 0 0 0 1px #edf2f7;
}

.web-title {
    text-align: center;
    font-size: 1.4rem;
    color: #2d3748;
    font-weight: bold;
    margin-bottom: 10px;
}

.web-question {
    text-align: center;
    margin-bottom: 20px;
    color: #4a5568;
    font-size: 1.1rem;
}

.web-input {
    width: 100%;
    padding: 12px;
    border: 2px solid #cbd5e0;
    border-radius: 8px;
    font-size: 1rem;
    text-align: center;
    margin-bottom: 20px;
}

.web-button {
    background: #3182ce;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    font-size: 1rem;
    width: 100%;
}

.web-image {
    text-align: center;
    margin: 15px 0;
}

.web-image img {
    max-width: 200px;
    max-height: 200px;
    border-radius: 8px;
    border: 2px solid #cbd5e0;
    object-fit: contain;
}

.web-result {
    text-align: center;
    padding: 12px;
    border-radius: 8px;
    margin-top: 15px;
}

.web-result.success {
    background: #c6f6d5;
    color: #2f855a;
}

.web-result.error {
    background: #fed7d7;
    color: #e53e3e;
}

.web-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
}

.web-option {
    background: #e2e8f0;
    color: #2d3748;
    border: 2px solid #cbd5e0;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    font-size: 1rem;
    transition: all 0.2s ease;
}

.web-option:hover {
    background: #cbd5e0;
    border-color: #a0aec0;
}

.web-option.selected {
    background: #90cdf4;
    border-color: #3182ce;
    color: #1a365d;
    font-weight: bold;
}

.web-option.disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
}

.web-next-button {
    background: #3182ce;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    font-size: 1rem;
    width: 100%;
    margin-top: 15px;
    transition: background 0.2s ease;
}

.web-next-button:hover {
    background: #2c5aa0;
}

.web-finish-button {
    background: #27ae60;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    font-size: 1rem;
    width: 100%;
    margin-top: 15px;
    transition: background 0.2s ease;
}

.web-finish-button:hover {
    background: #219653;
}

.note-section {
    background: white;
    border-radius: 18px;
    padding: 30px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    margin-bottom: 40px;
}

.note-section h2 {
    text-align: center;
    color: #2c5282;
    margin-bottom: 20px;
    font-size: 1.8rem;
}

.note-content {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
    font-size: 1.1rem;
    color: #4a5568;
    line-height: 1.8;
}

.highlight-text {
    background: #fef3c7;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: bold;
    color: #92400e;
}
</style>
