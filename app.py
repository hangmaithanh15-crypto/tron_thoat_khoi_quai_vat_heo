import base64
import os
import streamlit as st


def get_image_base64(path):
  if os.path.exists(path):
    with open(path, "rb") as f:
      encoded = base64.b64encode(f.read()).decode("utf-8")
      ext = path.split(".")[-1].lower()
      mime = "image/png" if ext == "png" else "image/jpeg"
      return f"data:{mime};base64,{encoded}"
  return ""


player_b64 = get_image_base64("player.png")
monster_b64 = get_image_base64("monster.png")
bg_b64 = get_image_base64("background.png")

st.set_page_config(
    page_title="Temple Run: Chạy Trốn Heo Peppa", page_icon="🏃‍♂️", layout="centered"
)

st.title("🏃‍♂️ Temple Run: Chạy Trốn Quái Vật Heo Peppa")
st.markdown(
    "Dùng phím **Trái (← / A)** và **Phải (→ / D)** để né chướng ngại vật!"
)

game_html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Temple Run - Tralalero vs Peppa Pig</title>
    <style>
        body {{
            background-color: #0e1117;
            color: white;
            text-align: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
        }}
        canvas {{
            background: #111;
            display: block;
            margin: 0 auto;
            border-radius: 12px;
            box-shadow: 0 0 25px rgba(255, 75, 75, 0.4);
        }}
        .controls {{
            margin-top: 15px;
        }}
        .btn {{
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 12px 28px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            margin: 0 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            transition: all 0.2s;
        }}
        .btn:hover {{
            background-color: #ff2222;
            transform: scale(1.05);
        }}
        .level-select {{
            margin-bottom: 10px;
        }}
        .level-btn {{
            background-color: #333;
            color: #fff;
            border: 2px solid #ff4b4b;
            padding: 8px 16px;
            margin: 0 5px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }}
        .level-btn.active {{
            background-color: #ff4b4b;
            color: white;
        }}
    </style>
</head>
<body>

    <!-- Nhạc nền Vết Thương (Fishy) -->
    <audio id="bgMusic" loop>
        <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mp3">
    </audio>

    <div class="level-select">
        <span style="font-weight:bold; margin-right:10px;">Chọn Cấp Độ:</span>
        <button class="level-btn active" id="lvl1" onclick="setLevel(1, 3.5, 90)">Cấp 1 (Dễ)</button>
        <button class="level-btn" id="lvl2" onclick="setLevel(2, 5.5, 70)">Cấp 2 (Vừa)</button>
        <button class="level-btn" id="lvl3" onclick="setLevel(3, 8.0, 50)">Cấp 3 (Khó)</button>
        <button class="level-btn" id="lvl4" onclick="setLevel(4, 11.5, 35)">Cấp 4 (Bá Khí)</button>
    </div>

    <canvas id="gameCanvas" width="600" height="500"></canvas>
    
    <div class="controls">
        <button class="btn" onclick="moveLeft()">◀ Trái</button>
        <button class="btn" onclick="moveRight()">Phải ▶</button>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const bgMusic = document.getElementById("bgMusic");

        // Load hình ảnh
        const playerImg = new Image();
        playerImg.src = "{player_b64}";

        const monsterImg = new Image();
        monsterImg.src = "{monster_b64}";

        const bgImg = new Image();
        bgImg.src = "{bg_b64}";

        // Cài đặt game & cấp độ
        let currentLevel = 1;
        let gameSpeed = 3.5;
        let spawnRate = 90;
        
        let score = 0;
        let gameOver = false;
        let gameStarted = false;

        // Tọa độ làn đường kiểu 3D Perspective (Đỉnh cao, Đáy rộng)
        const lanesBottom = [160, 300, 440];
        const lanesTop = [260, 300, 340];

        let playerLane = 1; 
        let playerX = lanesBottom[playerLane];
        let playerY = 350; // Người chơi ở phía trước

        let monsterLane = 1;
        let monsterX = lanesBottom[monsterLane];
        let monsterY = 440; // Quái vật ở phía sau xa hơn

        let obstacles = [];
        let frameCount = 0;
        let roadOffset = 0;

        function setLevel(lvl, speed, rate) {{
            currentLevel = lvl;
            gameSpeed = speed;
            spawnRate = rate;
            document.querySelectorAll('.level-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('lvl' + lvl).classList.add('active');
            if(gameStarted) resetGame();
        }}

        window.addEventListener("keydown", function(e) {{
            if (!gameStarted && (e.code === "Space" || e.code === "Enter")) {{
                startGame();
                return;
            }}
            if (gameOver && e.code === "Space") {{
                startGame();
                return;
            }}
            if (!gameOver && gameStarted) {{
                if (e.code === "ArrowLeft" || e.code === "KeyA") moveLeft();
                if (e.code === "ArrowRight" || e.code === "KeyD") moveRight();
            }}
        }});

        function startGame() {{
            gameStarted = true;
            resetGame();
            bgMusic.play().catch(e => console.log("Music play blocked by browser"));
        }}

        function moveLeft() {{
            if (playerLane > 0) playerLane--;
        }}

        function moveRight() {{
            if (playerLane < 2) playerLane++;
        }}

        function resetGame() {{
            score = 0;
            gameOver = false;
            obstacles = [];
            playerLane = 1;
            monsterLane = 1;
            gameStarted = true;
            bgMusic.currentTime = 0;
            bgMusic.play().catch(e => {{}});
        }}

        function update() {{
            if (!gameStarted || gameOver) return;

            // Di chuyển mượt người chơi
            let targetPlayerX = lanesBottom[playerLane];
            playerX += (targetPlayerX - playerX) * 0.25;

            // Quái vật Heo Peppa chạy đuổi theo làn đường của Player
            let targetMonsterX = lanesBottom[playerLane];
            monsterX += (targetMonsterX - monsterX) * 0.08; 

            // Cuộn đường Temple
            roadOffset = (roadOffset + gameSpeed) % 40;

            // Sinh chướng ngại vật ngẫu nhiên
            frameCount++;
            if (frameCount % Math.floor(spawnRate) === 0) {{
                let lane = Math.floor(Math.random() * 3);
                let type = Math.floor(Math.random() * 3); // 0: Đá, 1: Rào gỗ, 2: Gai
                obstacles.push({{ lane: lane, progress: 0, type: type, passed: false }});
            }}

            // Cập nhật chướng ngại vật
            for (let i = obstacles.length - 1; i >= 0; i--) {{
                let obs = obstacles[i];
                obs.progress += gameSpeed * 0.0035; // Tiến từ xa về gần

                // Tọa độ Y & X thực tế dựa theo phối cảnh
                let currentY = 120 + obs.progress * (400 - 120);
                let currentX = lanesTop[obs.lane] + obs.progress * (lanesBottom[obs.lane] - lanesTop[obs.lane]);

                // Kiểm tra va chạm khi đến vị trí người chơi
                if (obs.progress >= 0.65 && obs.progress <= 0.85) {{
                    if (obs.lane === playerLane) {{
                        gameOver = true;
                        bgMusic.pause();
                    }}
                }}

                // Tăng điểm khi vượt qua
                if (obs.progress > 0.85 && !obs.passed) {{
                    score += 10 * currentLevel;
                    obs.passed = true;
                }}

                if (obs.progress >= 1.0) {{
                    obstacles.splice(i, 1);
                }}
            }}
        }}

        function drawTempleRoad() {{
            // Nền trời / Xa xăm
            ctx.fillStyle = "#1b110a";
            ctx.fillRect(0, 0, canvas.width, 120);

            // Vẽ ảnh background mờ nếu có
            if (bgImg.complete && bgImg.naturalWidth !== 0) {{
                ctx.globalAlpha = 0.4;
                ctx.drawImage(bgImg, 0, 0, canvas.width, 180);
                ctx.globalAlpha = 1.0;
            }}

            // Con đường 3D Temple Run
            ctx.fillStyle = "#8d6e63";
            ctx.beginPath();
            ctx.moveTo(220, 120);
            ctx.lineTo(380, 120);
            ctx.lineTo(540, 500);
            ctx.lineTo(60, 500);
            ctx.closePath();
            ctx.fill();

            // Tường đá hai bên
            ctx.strokeStyle = "#4e342e";
            ctx.lineWidth = 12;
            ctx.beginPath();
            ctx.moveTo(220, 120); ctx.lineTo(60, 500);
            ctx.moveTo(380, 120); ctx.lineTo(540, 500);
            ctx.stroke();

            // Vạch gạch trên con đường
            ctx.strokeStyle = "#6d4c41";
            ctx.lineWidth = 3;
            for (let y = 120 + (roadOffset % 30); y < 500; y += 30) {{
                let p = (y - 120) / (500 - 120);
                let xLeft = 220 - p * 160;
                let xRight = 380 + p * 160;
                ctx.beginPath();
                ctx.moveTo(xLeft, y);
                ctx.lineTo(xRight, y);
                ctx.stroke();
            }}
        }}

        function drawObstacle(obs) {{
            let p = obs.progress;
            let currentY = 120 + p * (500 - 120);
            let currentX = lanesTop[obs.lane] + p * (lanesBottom[obs.lane] - lanesTop[obs.lane]);
            let size = 15 + p * 45; // Phóng to dần khi đến gần

            if (obs.type === 0) {{
                // Tảng đá lớn (Rock)
                ctx.fillStyle = "#5d4037";
                ctx.beginPath();
                ctx.arc(currentX, currentY, size, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#3e2723";
                ctx.lineWidth = 3;
                ctx.stroke();
            }} else if (obs.type === 1) {{
                // Rào cản gỗ (Barricade)
                ctx.fillStyle = "#d84315";
                ctx.fillRect(currentX - size, currentY - size / 2, size * 2, size);
                ctx.strokeStyle = "#fff";
                ctx.lineWidth = 2;
                ctx.strokeRect(currentX - size, currentY - size / 2, size * 2, size);
            }} else {{
                // Bẫy gai (Spikes)
                ctx.fillStyle = "#c62828";
                ctx.beginPath();
                ctx.moveTo(currentX - size, currentY + size/2);
                ctx.lineTo(currentX, currentY - size);
                ctx.lineTo(currentX + size, currentY + size/2);
                ctx.closePath();
                ctx.fill();
            }}
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Vẽ con đường Temple Run
            drawTempleRoad();

            if (!gameStarted) {{
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#ff4b4b";
                ctx.font = "bold 32px Arial";
                ctx.textAlign = "center";
                ctx.fillText("TEMPLE RUN: CÁ MẬP VS HEO PEPPA", canvas.width / 2, 180);
                ctx.fillStyle = "white";
                ctx.font = "18px Arial";
                ctx.fillText("Chọn cấp độ bên trên & Nhấn phím Cách (Space) để chơi", canvas.width / 2, 250);
                return;
            }}

            // 2. Vẽ chướng ngại vật
            for (let obs of obstacles) {{
                drawObstacle(obs);
            }}

            // 3. Vẽ Quái vật Heo Peppa (Đuổi phía sau)
            if (monsterImg.complete && monsterImg.naturalWidth !== 0) {{
                ctx.drawImage(monsterImg, monsterX - 45, monsterY - 40, 90, 80);
            }} else {{
                ctx.fillStyle = "pink";
                ctx.fillRect(monsterX - 35, monsterY - 35, 70, 70);
            }}

            // 4. Vẽ Người chơi Tralalero (Chạy phía trước)
            if (playerImg.complete && playerImg.naturalWidth !== 0) {{
                ctx.drawImage(playerImg, playerX - 30, playerY - 40, 60, 65);
            }} else {{
                ctx.fillStyle = "#0288d1";
                ctx.fillRect(playerX - 25, playerY - 35, 50, 50);
            }}

            // 5. Bảng điểm số & Cấp độ
            ctx.fillStyle = "white";
            ctx.font = "bold 20px Arial";
            ctx.textAlign = "left";
            ctx.fillText("Điểm: " + score, 20, 35);
            ctx.fillText("Cấp độ: " + currentLevel, 20, 65);

            // 6. Màn hình Game Over
            if (gameOver) {{
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "#ff4b4b";
                ctx.font = "bold 34px Arial";
                ctx.textAlign = "center";
                ctx.fillText("BẠN ĐÃ BỊ HEO PEPPA ĂN THỊT!", canvas.width / 2, 200);
                ctx.fillStyle = "white";
                ctx.font = "22px Arial";
                ctx.fillText("Tổng điểm của bạn: " + score, canvas.width / 2, 250);
                ctx.fillText("Nhấn phím Cách (Space) để Chơi lại", canvas.width / 2, 310);
            }}
        }}

        function loop() {{
            update();
            draw();
            requestAnimationFrame(loop);
        }}

        loop();
    </script>
</body>
</html>
"""

st.components.v1.html(game_html, height=620)
