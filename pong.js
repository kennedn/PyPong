//Extends number prototype to include clipping method
Number.prototype.clip = function(min, max) {
  return Math.min(Math.max(this, min), max);
};

//Helping function for checking collision between two proto-rects
function colliding(pos1, size1, pos2, size2) {
	//r1Right > r2Left and r1Left < r2Right
	//r1Bot > r2Top and r1Top < r2Bottom
	if (pos1.x + size1.x > pos2.x && pos1.x < pos2.x + size2.x &&
		pos1.y + size1.y > pos2.y && pos1.y < pos2.y + size2.y)
		return true;
	return false;
}


/**
  * @desc Defines a rectangle that follows a provided target vector on the y axis
  * @param float pos_x - x position
  * @param float pos_y - y position
  * @param float size_x - width
  * @param float size_y - height
  * @param float speed - movement speed
  * @param float threshold - dead zone to prevent jitter when following target
*/
class Paddle {
	constructor(pos_x, pos_y, size_x, size_y, speed, threshold) {
		this.position = createVector(pos_x, pos_y);
		this.size = createVector(size_x, size_y);
		this.speed = speed;
		this.threshold = threshold;
		this.velocity = createVector(0, 0);
		this.center = createVector(0, 0);
	}

	move_up() {
		this.velocity.set(this.velocity.x, -this.speed);
	}
	move_down() {
		this.velocity.set(this.velocity.x, this.speed);
	}
	speed_reset() {
		this.velocity.set(this.velocity.x, 0);
	}

	// target is a vector that we want our pad to follow in y axis
	update(target) {
		// update center based on current position
		this.center.set(this.position.x + this.size.x / 2, 
						this.position.y + this.size.y / 2);

		// distance to target is within threshold
		if (abs(target.y - this.center.y) <= this.threshold)
			this.speed_reset();
		// target is below paddle
		else if (target.y > this.center.y)
			this.move_down();
		// target is above paddle
		else if(target.y < this.center.y)
			this.move_up();

		// update y position based on current velocity, clip to bounds of canvas
		this.position.set(this.position.x, 
						  (this.position.y + this.velocity.y * (deltaTime / (1/speed))).clip(0, height - this.size.y));
	}

	draw() {
		rect(this.position.x, this.position.y, this.size.x, this.size.y);
	}
}


/**
  * @desc Defines a moving ball that collides with top,bottom and paddles
  * @param float size_x - width
  * @param float size_y - height
  * @param float speed - movement speed
  * @param int delay_ms - time to wait for ball launch after reset
*/
class Ball {
	constructor(size_x, size_y, speed, delay_ms) {
		this.init = createVector(width / 2 - size_x / 2, height /2 - size_y /2);
		this.size = createVector(size_x, size_y);
		// tracks player score
		this.score = [0, 0];
		this.speed = speed;
		this.delay_ms = delay_ms;
		this.delay_counter = 0;
		this.position = createVector(0, 0);
		this.velocity = createVector(0, 0);
		this.center = createVector(0, 0);
		this.reset_ball(false);
	}
	// resets ball to center screen with a random velocity
	reset_ball(score_assign = true) {
		// check ball position and award point to correct player.
		if (score_assign) {
			if (this.center.x <= 0)
				this.score[1] += 1;
			else if (this.center.x >= width)
				this.score[0] += 1;
		}

		this.delay_counter = 0;
		this.position.set(this.init.x, this.init.y);
		// Set ball velocity to random trajectory
		this.velocity.set(random([this.speed, -this.speed]), random(this.speed * 1.5, -this.speed * 1.5));
	}

	// Helper class for switching ball velocity upon hitting a paddle
	paddle_strike(direction, pad_center_y) {
		// Determine a scaler value, roughly between -0.2 and -1 based on
		// distance from center of pad
		let scaler = -(1 + pad_center_y - this.center.y) / (this.size.y / 2);

		// Explicitly set a passed direction for x to ensure we don't get stuck 
		// inside a paddle. Set y based on current velocity plus a nudge from our scaler
		this.velocity.set(this.speed * direction,
						  this.velocity.y + this.speed * 0.15 * scaler);
	}

	update() {
		// Update center based on current position
		this.center.set(this.position.x + this.size.x / 2, 
						this.position.y + this.size.y / 2);
		this.delay_counter += deltaTime;
		// hitting top wall
		if (this.position.y < 0) {
			// explicitly move ball out of check zone so we don't get stuck in the wall
			this.position.set(this.position.x, 0);
			//reverse y velocity
			this.velocity.set(this.velocity.x, -this.velocity.y);
		}
		// hitting bottom wall
		else if (this.position.y + this.size.y > height) {
			// explicitly move ball out of check zone so we don't get stuck in the wall
			this.position.set(this.position.x, height - this.size.y);
			//reverse y velocity
			this.velocity.set(this.velocity.x, -this.velocity.y);
		}
		// out of x bounds
		else if (this.position.x + this.size.x <= 0 || this.position.x >= width)
			this.reset_ball();
		// not colliding with canvas (out of bounds for some reason)
		else if (!colliding(this.position, this.size, createVector(0, 0), createVector(width, height)))
			this.reset_ball(false);

		if (this.delay_counter >= this.delay_ms) {
			// update position basedo on velocity
			this.position.set(this.position.x + this.velocity.x * (deltaTime / (1/speed)),
							  this.position.y + this.velocity.y * (deltaTime / (1/speed)));
		}
	}

	draw() {
		rect(this.position.x, this.position.y, this.size.x, this.size.y);
	}
}


let DEBUG = 1;
let speed;
let mouseVect;

let pad1;
let pad2;
let ball;

let font;
function preload() {
	font = loadFont('Pixeled.ttf');
}

function setup() {
  createCanvas(480, 320);
  
  pad1 = new Paddle(20, 60, 10, 50, 1, 10);
  pad2 = new Paddle(width - 20 - 10, 60, 10, 50, 1.005, 10);
  ball = new Ball(10, 10, 1.05, 450);

  speed = 0.15;
  mouseVect = createVector(mouseX, mouseY);
  stroke(255);
  fill(255);
  textFont(font);
  textAlign(CENTER);
  textSize(32);
}

function keyPressed() {
	if (DEBUG > 0) {
		if (key === '1')
			ball.score[0] += 5;
		else if (key === '2')
			ball.score[0] -= 5;
		else if (key === '3')
			ball.score = [0, 0];
	}
}

function draw() {
	// fill screen
	background(0);
	// store current mouse vector
	mouseVect.set(mouseX, mouseY);
	
	ball.update();
	// pad1 will follow mouse
	pad1.update(mouseVect);
	// pad2 will follow ball
	pad2.update(ball.center);
	update();

	// draw center dotted line
	strokeWeight(4);
	for(let y = 0; y < height; y+=15)
		if (y % 2 == 0)
			line(width / 2, y, width / 2, y + 15);
	strokeWeight(0);

	// draw each player score, clip to 99 and add leading 0 if less than 10
	score = ball.score[0].clip(0, 99);
	text(score >= 10 ? score : "0" + str(score), width * 0.25, 50);
	score = ball.score[1].clip(0, 99);
	text(score >= 10 ? score : "0" + str(score), width * 0.75, 50);

	ball.draw();
	pad1.draw();
	pad2.draw();
}

// Mostly collision
function update() {
	// Calculate some smaller face rects for collision checks to stop collision happening
	// when the ball touches the back portion of a paddle.
	let pad1_face_pos = createVector(pad1.position.x + pad1.size.x - 2, pad1.position.y);
	let pad1_face_size = createVector(2,pad1.size.y);
	let pad2_face_size = createVector(2,pad2.size.y);
	// if ball and pad1 are colliding
	if (colliding(ball.position, ball.size, pad1_face_pos, pad1_face_size))
		// inform ball class of the strike so it can adjust velocity accordingly
		ball.paddle_strike(1, pad1.center.y);
	// if ball and pad2 are colliding
	else if (colliding(ball.position, ball.size, pad2.position, pad2_face_size))
		// inform ball class of the strike so it can adjust velocity accordingly
		ball.paddle_strike(-1, pad2.center.y);
}

