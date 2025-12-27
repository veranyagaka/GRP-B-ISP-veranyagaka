const redis = require('redis');

const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redisClient.on('error', (err) => console.error('Redis Error:', err));

(async () => {
  try {
    await redisClient.connect(); // Must connect first
    console.log('✅ Redis connected');

    // Set key/value
    await redisClient.set('ChannelName', 'Codespace');

    // Get value
    const value = await redisClient.get('ChannelName');
    console.log('Value:', value); // Should print 'Codespace'

    await redisClient.quit(); // Close connection
  } catch (err) {
    console.error('Redis connection failed:', err);
  }
})();
