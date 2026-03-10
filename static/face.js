/* =========================================
SHADOW AI FACE AUTH SCRIPT (FINAL)
========================================= */

if (typeof faceapi === "undefined") {
console.error("FaceAPI failed to load");
alert("Face recognition library failed to load. Refresh the page.");
}

let stream = null;

/* =========================================
CAMERA CONTROL
========================================= */

async function openCamera(){

```
const modal = document.getElementById("faceModal");

modal.style.display = "flex";

try{

    stream = await navigator.mediaDevices.getUserMedia({
        video:true
    });

    const video = document.getElementById("video");

    video.srcObject = stream;

}catch(err){

    console.error(err);
    alert("Camera access denied");

}
```

}

function closeCamera(){

```
const modal = document.getElementById("faceModal");

modal.style.display = "none";

if(stream){

    stream.getTracks().forEach(track=>{
        track.stop();
    });

}
```

}

/* =========================================
CAPTURE FRAME
========================================= */

function captureFrame(){

```
const video = document.getElementById("video");

const canvas = document.createElement("canvas");

canvas.width = video.videoWidth;
canvas.height = video.videoHeight;

const ctx = canvas.getContext("2d");

ctx.drawImage(video,0,0);

return canvas.toDataURL("image/png");
```

}

/* =========================================
REGISTER FACE
========================================= */

async function registerFace(){

```
const usernameInput = document.getElementById("username");

if(!usernameInput){
    alert("Username field not found");
    return;
}

const username = usernameInput.value.trim();

if(!username){
    alert("Enter username first");
    return;
}

await openCamera();

setTimeout(async()=>{

    const image = captureFrame();

    try{

        const res = await fetch("/register_face",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                username:username,
                image:image
            })
        });

        const data = await res.json();

        closeCamera();

        if(data.success){
            alert("Face registered successfully");
        }
        else{
            alert("Face registration failed");
        }

    }catch(error){

        console.error(error);
        closeCamera();
        alert("Server error during registration");

    }

},2000);
```

}

/* =========================================
FACE LOGIN
========================================= */

async function faceLogin(){

    await openCamera()

    setTimeout(async()=>{

        const image = captureFrame()

        const res = await fetch("/face_login",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                image:image
            })
        })

        const data = await res.json()

        closeCamera()

        if(data.success){

            const screen = document.getElementById("welcomeScreen")
            const msg = document.getElementById("welcomeMessage")

            msg.innerText = "WELCOME " + data.name.toUpperCase()

            screen.style.display = "flex"

            // redirect after message
            setTimeout(function(){

                window.location.href = "/"

            },3000)

        }else{

            alert("Face not recognized")

        }

    },2000)

}