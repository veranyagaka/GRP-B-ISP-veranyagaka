const express =require('express');
const router =express.Router();
const path = require('path');

const database = require('../db.js');

// Catch-all handler to return the React router
router.get('/login', (req, res) => {
  res.render('login2');
});

router.get('/register', (req, res) => {
  res.render('register');
  });
// Login route
router.post('/login', async (req, res) => {
    const { employeeID, password } = req.body;
    try {
      const [result] = await database.query(
        'SELECT * FROM Employee WHERE EmployeeID = ?',
        [employeeID]
      );
      console.log('Queried user:', result);
      if (!result.length) {
        return res.render('login', { error: 'Incorrect Employee ID or Password.' });
      }
      const email = result[0].email 
      const validPassword = await bcrypt.compare(password, result[0].password);
  
      if (!validPassword) {
        return res.render('login', { error: 'Incorrect Employee ID or Password.' });
      }
            console.log('Stored Password:', result[0].password);
            //maybe jwt functionality?
            req.session.EmployeeID = result[0].EmployeeID;
            req.session.save(async (err) => {
              if (err) {
                console.error(err);
              } else {
                console.log('Session saved:', req.session.EmployeeID);
                const subject = 'New login detected!';
                const message = `Hi there! New sign in to your PayMaster account <br> If this was you, then you don't need to do anything. <br>If you don't recognise this activity, please change your password.`;
                res.redirect('employee-profile');
              }
            });
          } catch (err) {
            console.error(err);
            res.status(500).json({ error: 'Internal server error' });
          }
        });
// Register route
router.post('/register', async (req, res) => {
  const { email, password } = req.body;
  console.log(`Received email: ${email}, password: ${password}`);

  if (!email || !password) {
    return res.status(400).send('Email and password are required');
  }
  const existingUserSql = 'SELECT * FROM Employee WHERE email = ?';

  try {
    const [rows] = await database.query(existingUserSql, [email]);
    if (rows.length > 0) {
      return res.status(409).send('Email already exists');
    }
  } catch (err) {
    console.error(err);
    return res.status(500).send('Internal server error');
  }

  // Hash password before storing
  const saltRounds = 10; // Adjust salt rounds for security
  const hashedPassword = await bcrypt.hash(password, saltRounds);

  const sql = 'INSERT INTO Employee (email, password) VALUES (?, ?)';

  try {
    const result = await database.query(sql, [email, hashedPassword]);
    const employeeID = result[0].insertId;
    const profile = 'INSERT INTO employee_profile (employeeID, email) VALUES (?,?)';
    await database.query(profile, [employeeID, email]);
    const subject = 'Welcome to Paymaster';
    const message = `
    Hi there! You've successfully registered for an account. Your employee ID is ${employeeID}.
  `;
  
    setTimeout(() => {
      res.redirect('/login');
    }, 3000); 
  } catch (err) {
    console.error(err);
    res.status(500).send('Registration failed');
  }
  //
});

//admin page
function isAuthenticated(req, res, next) {
  if (req.session.adminId) {
    return next();
  } else {
    req.flash('error', 'You need to be logged in to view this page');
    res.redirect('/admin-login');
  }
}
router.get('/admin-login', (req, res) => {
  res.render('admin-login');
});
router.post('/admin-login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const [result] = await database.query(
      'SELECT * FROM admin WHERE email = ?',
      [email]
    );
    console.log('Queried admin:', result);
    if (!result.length) {
      return res.render('admin-login', { error: 'Incorrect email or Password.' });;   
    }

    const validPassword = await bcrypt.compare(password, result[0].password);

    if (!validPassword) {
      return res.render('admin-login', { error: 'Incorrect email or Password.' });;   
   }
          req.session.adminId = result[0].id;  // Set admin ID in session
          console.log('Stored Password:', result[0].password);
          console.log('session check' ,req.session.adminId)
          return res.redirect('/admin');
     } catch (err) {
          console.error(err);
          res.status(500).json({ error: 'Internal server error' });
        }
      });
// const adminRouter =require('./routes/admin')
// router.use('/admin',isAuthenticated, adminRouter)

router.get('/employee-profile', async (req, res) => {
  req.flash('success', 'Login successful!');

  console.log('Session check employeeID:', req.session.EmployeeID);
  if (!req.session.EmployeeID) {
    return res.status(401).redirect('/login'); // Redirect to login if no session
  }
  try {
      const [rows] = await database.query('SELECT * FROM employee_profile WHERE employeeID = ?', [req.session.EmployeeID]);
      const employee = rows[0];
      if (!employee) {
        return res.status(404).send('Employee profile not found');
      }
      async function getPaymentDetailsByEmployeeId(employeeID) {
        const query = 'SELECT * FROM paymentdetails WHERE employeeID = ?';
        const [rows] = await database.query(query, [employeeID]);
        return rows;
      }
      const paymentDetails = await getPaymentDetailsByEmployeeId(req.session.EmployeeID);
      const showPaymentButton = paymentDetails.length == 0;
      console.log(showPaymentButton);
      const location =(path.join(__dirname, '../frontend/public'));
      console.log(location)
      res.render('employee-profile', { employee: employee, showPaymentButton: showPaymentButton, location });
  } catch (err) {
      console.error(err);
      res.status(500).send('Internal Server Error');
  }
});
router.get('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      console.error(err);
      return res.status(500).send('Internal Server Error');
    }
    res.redirect('/login');
  });
});

router.use((req, res, next) => {
  res.status(404).render('404');
});

// Google Authentication Route
router.post('/auth/google', async (req, res) => {
  try {
    const { token } = req.body;

    // Verify Google ID token using Firebase Admin
    const decodedToken = await admin.auth().verifyIdToken(token);
    const email = decodedToken.email;
    const name = decodedToken.name;
    const googleUid = decodedToken.uid;

    console.log("Google user:", decodedToken);

    // Check if the user exists in MySQL
    const [existing] = await database.query('SELECT * FROM Employee WHERE email = ?', [email]);

    let employeeID;

    if (existing.length > 0) {
      employeeID = existing[0].EmployeeID;
    } else {
      // If not, insert new Google user
      const [insertResult] = await database.query(
        'INSERT INTO Employee (email, google_uid, name) VALUES (?, ?, ?)',
        [email, googleUid, name]
      );
      employeeID = insertResult.insertId;

      const profile = 'INSERT INTO employee_profile (employeeID, email) VALUES (?, ?)';
      await database.query(profile, [employeeID, email]);
    }

    // Create session for this user
    req.session.EmployeeID = employeeID;
    req.session.save((err) => {
      if (err) {
        console.error('Session save error:', err);
        return res.status(500).send('Session error');
      }
      res.status(200).json({ message: 'Google login successful', employeeID });
    });
  } catch (err) {
    console.error('Google Auth error:', err);
    res.status(401).json({ error: 'Invalid Google token' });
  }
});

// Google/Firebase Login (login2)
router.post('/login2', async (req, res) => {
  try {
    const { idToken } = req.body; // token sent from frontend after Google sign-in
    if (!idToken) {
      return res.status(400).json({ error: 'Missing ID token' });
    }

    // Verify the token using Firebase Admin SDK
    const decodedToken = await admin.auth().verifyIdToken(idToken);
    const { uid, email, name, picture } = decodedToken;

    console.log('Verified Firebase user:', decodedToken);

    // Check if the user exists
    const [existing] = await database.query(
      'SELECT * FROM Employee WHERE email = ?',
      [email]
    );

    let employeeID;

    if (existing.length > 0) {
      // User exists
      employeeID = existing[0].EmployeeID;
      console.log(`Existing user logged in: ${email}`);
    } else {
      // Create new Employee record
      const [insertResult] = await database.query(
        'INSERT INTO Employee (full_name, email, firebase_uid) VALUES (?, ?, ?)',
        [name || 'Unknown', email, uid]
      );
      employeeID = insertResult.insertId;

      console.log(`New Firebase user added: ${email} (ID: ${employeeID})`);
    }

    // Create a session
    req.session.EmployeeID = employeeID;
    req.session.save((err) => {
      if (err) {
        console.error('Session save error:', err);
        return res.status(500).json({ error: 'Failed to save session' });
      }

      res.status(200).json({
        message: 'Firebase login successful',
        employeeID,
        name,
        email,
        picture,
      });
    });
  } catch (error) {
    console.error('Firebase login2 error:', error);
    res.status(401).json({ error: 'Invalid or expired Firebase token' });
  }
});


module.exports= router