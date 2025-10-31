import express from "express"
import mongoose from "mongoose"
import cors from 'cors';

const app = express();
app.use(express.json());
app.use(express.urlencoded());
app.use(cors())



mongoose.connect("mongodb://127.0.0.1/Userregistration",
    // {
    //     useNewUrlParser: true,
    //     useNewUnifiedTopology: true
    // }

).then((res) => {
    if (res) {
        console.log("database connected!!")
    }
}).catch((err) => { console.log(err) })



const userschema = new mongoose.Schema({
    username: String,
    password: String
})


const signup = new mongoose.model("userdata", userschema)



app.get("/", (req, res) => {
    res.send("backend server started")
});

app.post("/signup", (req, res) => {

    console.log("data from frontend", req.body);

    signup.findOne({ username: req.body.username }).then(
        (resp) => {
            if (resp) {
                res.send("user account already present")
            }
            else {

                const newuser = signup({
                    username: req.body.username,
                    password: req.body.password
                })

                newuser.save().then((ack) => {
                    if (ack) {
                        res.send("registered successfully")
                    }
                    else {
                        res.send("error in creating!!")
                    }


                }).catch((err) => { console.log(err) })


            }
        }
    )


}
)

app.listen(7000,()=>{
    console.log("Server runnig at port no 7000")
})