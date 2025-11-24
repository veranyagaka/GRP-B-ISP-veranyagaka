const express = require('express');
const app = express();
const port = process.env.PORT || 2000;
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const mysql = require('mysql2');
const path = require('path');
const cors = require('cors');
const bodyParser = require('body-parser');
const session = require('express-session');
const flash = require('connect-flash');

const database = require('./db.js');

const admin = require('./firebase');
app.use(bodyParser.urlencoded({ extended: true })); 
app.use(bodyParser.json());
const corsOptions = {
  origin: ['https://your-frontend-app.com', 'http://localhost:2000'],
  optionsSuccessStatus: 200,
  allowedHeaders: ['Content-Type', 'Authorization']

};
app.get('/test', async (req, res) => {
  try {
    const [rows] = await database.query('SELECT 1');
    res.send('Database connection successful!');
  } catch (err) {
    res.status(500).send('Database connection failed');
  }
});

app.use(cors(corsOptions));
//enables cors
app.use(cors({
  'allowedHeaders': ['sessionId', 'Content-Type'],
  'exposedHeaders': ['sessionId'],
  'origin': '*',
  'methods': 'GET,HEAD,PUT,PATCH,POST,DELETE',
  'preflightContinue': false
}));

app.set('view engine', 'ejs');
// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, '../frontend/views'));
app.use(express.static(path.join(__dirname, '../frontend/public'))); // CSS/JS/images
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

app.use(express.json());

// routes

// feedback route
app.get('/feedback', (req, res) => {
    res.render('feedback');
});

app.post('/feedback', (req, res) => {
    const { message } = req.body;
    console.log(message)
    // if (!message || message.trim() === "") {
    //     return res.render('feedback', { error: "Please enter a message." });
    // }

    const sql = "INSERT INTO feedback (message) VALUES (?)";

    database.query(sql, [message], (err, result) => {
        if (err) {
            console.log(err);
            return res.render('feedback', { error: "Something went wrong." });
        }

        res.render('dashboard', { success: "Feedback submitted successfully!" });
    });
});

const predictionRoutes = require('./routes/prediction');
app.use('/', predictionRoutes);

const resolutionRoutes = require("./routes/resolution");
app.use("/", resolutionRoutes);

const authRoutes = require("./routes/auth");
app.use("/auth", authRoutes);



const redis = require('redis');
const RedisStore = require("connect-redis").default;
const redisClient = redis.createClient({
    url: process.env.REDIS_URL   // Timeout in milliseconds (300,000 ms = 5 minutes)
}
);
redisClient.connect()
  .then(() => console.log('Redis client connected'))
  .catch(console.error);
let redisStore = new RedisStore({
    client: redisClient,
});
app.use(session({
  store: redisStore,
  secret: process.env.SESSION_SECRET || 'your_secret_key_here',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false, maxAge: 1000 * 60 * 60 } // Expires in 1 hour
}));
// Example route to test session
app.get('/redis', (req, res) => {
  if (req.session.views) {
    req.session.views++;
    res.setHeader('Content-Type', 'text/html');
    res.write('<p>Views: ' + req.session.views + '</p>');
    res.write('<p>Expires in: ' + (req.session.cookie.maxAge / 1000) + 's</p>');
    res.end();
  } else {
    req.session.views = 1;
    res.end('Welcome to the session demo. Refresh!');
  }
});
app.get('/redis-test', async (req, res) => {
  try {
    await redisClient.set('test-key', 'test-value');
    const value = await redisClient.get('test-key');
    res.send(`Redis is working! Value: ${value}`);
  } catch (err) {
    res.status(500).send('Redis error: ' + err.message);
  }
});


app.use(flash());

app.use((req, res, next) => {
  res.locals.error = req.flash('error');
  res.locals.success = req.flash('success');
  next();
});

app.get('/', (req, res) => {
  res.render('index');
});
app.get('/dashboard', (req, res) => {
  res.render('dashboard');
});




app.listen(port, () => {
    console.log(`PayMaster app listening at http://localhost:${port}`);
});

