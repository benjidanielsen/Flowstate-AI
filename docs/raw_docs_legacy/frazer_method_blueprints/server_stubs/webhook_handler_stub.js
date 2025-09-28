// webhook_handler_stub.js (eksempel)
const express = require('express'); const app = express(); app.use(express.json());
app.post('/hooks/dm', (req,res)=>{
  const p = req.body;
  // map → contact/deal/events
  return res.json({ok:true});
});
app.listen(3000, ()=> console.log('listening'));
