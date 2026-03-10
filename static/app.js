document.addEventListener("DOMContentLoaded", () => {

console.log("Shadow AI JS Loaded")

})

/* ===============================
   AI SPEAK FUNCTION
================================ */

window.speak = function(text){

// stop previous speech
window.speechSynthesis.cancel()

const utter = new SpeechSynthesisUtterance(text)

utter.rate = 1
utter.pitch = 1.1
utter.volume = 1
utter.lang = "en-US"

speechSynthesis.speak(utter)

}

/* =========================================================
ELEMENT REFERENCES
========================================================= */

const chat = document.getElementById("chat")
const form = document.getElementById("composerForm")
const input = document.getElementById("messageInput")

const clearBtn = document.getElementById("clearBtn")
const chatHistory = document.getElementById("chatHistory")
const modeIndicator = document.getElementById("modeIndicator")

const fileInput = document.getElementById("fileInput")
const uploadBtn = document.getElementById("uploadBtn")
const searchBtn = document.getElementById("searchBtn")
const researchBtn = document.getElementById("researchBtn")
const stopBtn = document.getElementById("stopBtn")
const newChatBtn = document.getElementById("newChatBtn")

const toolsToggle = document.getElementById("toolsToggle")
const toolsMenu = document.getElementById("toolsMenu")

const toolDns = document.getElementById("toolDns")
const toolIp = document.getElementById("toolIp")
const toolScan = document.getElementById("toolScan")
const toolGraph = document.getElementById("toolGraph")

const themeToggle = document.getElementById("themeToggle")

/* =========================================================
STATE
========================================================= */

let currentSessionId = null
let controller = null
let currentMode = "chat"

/* =========================================================
ENTER TO SEND
========================================================= */

if (input && form) {

input.addEventListener("keydown", function (e) {

if (e.key === "Enter" && !e.shiftKey) {
e.preventDefault()
form.dispatchEvent(new Event("submit"))
}

})

}

/* =========================================================
THEME
========================================================= */

if (localStorage.getItem("theme") === "light") {
document.body.classList.add("light")
themeToggle.textContent = "☀️"
}

themeToggle.addEventListener("click", function () {

document.body.classList.toggle("light")

if (document.body.classList.contains("light")) {
localStorage.setItem("theme", "light")
themeToggle.textContent = "☀️"
}
else {
localStorage.setItem("theme", "dark")
themeToggle.textContent = "🌙"
}

})

/* =========================================================
AUTO GROW TEXTAREA
========================================================= */

if (input) {

input.addEventListener("input", function () {

this.style.height = "auto"
this.style.height = this.scrollHeight + "px"

})

}

/* =========================================================
SCROLL
========================================================= */

function scrollToBottom() {

if (chat) {
chat.scrollTop = chat.scrollHeight
}

}

/* =========================================================
RENDER CONTENT
========================================================= */

function renderContent(content) {

if (!content) return ""

if (typeof marked !== "undefined") {

let html = marked.parse(content)
html = html.replace(/<a /g,'<a target="_blank" rel="noopener noreferrer" ')
return html

}

return content.replace(/\n/g,"<br>")

}

/* =========================================================
VOICE INPUT
========================================================= */

window.startVoice = function(){
  window.speechSynthesis.cancel()

const SpeechRecognition =
window.SpeechRecognition || window.webkitSpeechRecognition

if(!SpeechRecognition){
alert("Voice recognition not supported")
return
}

const recognition = new SpeechRecognition()

recognition.lang = "en-US"
recognition.continuous = false
recognition.interimResults = false

console.log("🎤 Listening...")

recognition.start()

recognition.onresult = function(event){

const transcript = event.results[0][0].transcript

console.log("Voice detected:", transcript)

if(input){
input.value = transcript
}

recognition.stop()

sendMessage(transcript,"chat")

}

recognition.onerror = function(event){

console.log("Voice error:", event.error)

}

}

/* =========================================================
VOICE REPLY
========================================================= */

function speakResponse(text){

if(!text) return

const speech = new SpeechSynthesisUtterance()

speech.text = text
speech.lang = "en-US"
speech.rate = 1
speech.pitch = 1

window.speechSynthesis.speak(speech)

}

/* =========================================================
CREATE MESSAGE BUBBLE
========================================================= */

function createBubble(role, content) {

const row = document.createElement("div")

row.className = role === "user"
? "row row-right"
: "row row-left"

const bubble = document.createElement("div")

bubble.className = role === "user"
? "bubble bubble-user"
: "bubble bubble-ai"

const body = document.createElement("div")
body.className = "content"
body.innerHTML = renderContent(content)

bubble.appendChild(body)
row.appendChild(bubble)

return row

}

/* =========================================================
MODE INDICATOR
========================================================= */

function updateModeIndicator(mode){

currentMode = mode

if(!modeIndicator) return

if(mode === "search"){
modeIndicator.textContent = "Mode: 🔎 Search"
}
else if(mode === "research"){
modeIndicator.textContent = "Mode: 🧠 Deep Research"
}
else{
modeIndicator.textContent = "Mode: 💬 Chat"
}

}

/* =========================================================
SEND MESSAGE
========================================================= */

async function sendMessage(text, mode = "chat") {

const hasFile = fileInput && fileInput.files.length > 0

if (!text || (!text.trim() && !hasFile)) return

updateModeIndicator(mode)

if (text.trim()) {

chat.appendChild(createBubble("user", text))
scrollToBottom()

}

const typing = createBubble("assistant", "Typing...")
typing.id = "typingIndicator"

chat.appendChild(typing)
scrollToBottom()

input.value = ""
input.style.height = "auto"
input.disabled = true

controller = new AbortController()

const formData = new FormData()

formData.append("text", text)
formData.append("session_id", currentSessionId || "")
formData.append("mode", mode)

if (hasFile) {
formData.append("file", fileInput.files[0])
}

try {

const response = await fetch("/api/message", {
method: "POST",
body: formData,
signal: controller.signal
})

const data = await response.json()

const indicator = document.getElementById("typingIndicator")
if (indicator) indicator.remove()

currentSessionId = data.session_id

if (data.assistant) {

chat.appendChild(createBubble("assistant", data.assistant))
scrollToBottom()

speakResponse(data.assistant)

}

}

catch (error) {

const indicator = document.getElementById("typingIndicator")
if (indicator) indicator.remove()

if (error.name === "AbortError") {
chat.appendChild(createBubble("assistant","⛔ Generation stopped."))
}
else {
chat.appendChild(createBubble("assistant","⚠️ Error occurred."))
}

}

finally {

stopBtn.classList.add("hidden")
input.disabled = false
input.focus()

}

fileInput.value = ""
loadSessions()

}

/* =========================================================
TOOLS MENU
========================================================= */

if (toolsToggle && toolsMenu) {

toolsToggle.addEventListener("click", function(e){

e.stopPropagation()
toolsMenu.classList.toggle("open")

})

document.addEventListener("click", function(){

toolsMenu.classList.remove("open")

})

}

/* =========================================================
TOOL SHORTCUTS
========================================================= */

if (toolDns){
toolDns.addEventListener("click", function(){
input.value = "dns "
input.focus()
})
}

if (toolIp){
toolIp.addEventListener("click", function(){
input.value = "ip "
input.focus()
})
}

if (toolScan){
toolScan.addEventListener("click", function(){
input.value = "scan "
input.focus()
})
}

if (toolGraph){
toolGraph.addEventListener("click", function(){
input.value = "create graph "
input.focus()
})
}

/* =========================================================
BUTTON EVENTS
========================================================= */

if (form) {
form.addEventListener("submit", function(e){
e.preventDefault()
sendMessage(input.value,"chat")
})
}

if (searchBtn){
searchBtn.addEventListener("click",function(){
sendMessage(input.value.trim(),"search")
})
}

if (researchBtn){
researchBtn.addEventListener("click",function(){
sendMessage(input.value.trim(),"research")
})
}

if (stopBtn){
stopBtn.addEventListener("click",function(){
if(controller) controller.abort()
})
}

if (uploadBtn){
uploadBtn.addEventListener("click",function(){
fileInput.click()
})
}

if (clearBtn){
clearBtn.addEventListener("click",function(){
chat.innerHTML = ""
})
}

/* =========================================================
NEW CHAT
========================================================= */

if (newChatBtn){

newChatBtn.addEventListener("click", async function(){

const response = await fetch("/api/session",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({title:"New Chat"})
})

const data = await response.json()

currentSessionId = data.session_id
chat.innerHTML = ""

loadSessions()

})

}

/* =========================================================
LOAD SESSION
========================================================= */

async function loadSession(sessionId){

currentSessionId = sessionId

const response = await fetch(`/api/session/${sessionId}`)
const data = await response.json()

chat.innerHTML = ""

data.messages.forEach(function(msg){

chat.appendChild(createBubble(msg.role,msg.content))

})

scrollToBottom()
loadSessions()

}

/* =========================================================
LOAD SESSIONS
========================================================= */

async function loadSessions(){

const response = await fetch("/api/sessions")
const data = await response.json()

chatHistory.innerHTML = ""

data.sessions.forEach(function(session){

const div = document.createElement("div")

div.className = "chat-item"
div.textContent = session.title

if(session.id === currentSessionId){
div.classList.add("active")
}

div.onclick = function(){
loadSession(session.id)
}

chatHistory.appendChild(div)

})

}


