const sign = document.querySelector('.su');
const disp = document.querySelector('.sign');
const login = document.querySelector('.log2');
const prevent = document.querySelector('.lo2');
const log = document.querySelector('.lo');
sign.addEventListener('click' ,()=>{
    disp.classList.add('log');
    login.classList.remove('log');
});


prevent.addEventListener('click',()=>{
    disp.classList.add('log');
});

// log.addEventListener('click',()=>{
//     login.classList.add('log');
//     disp.classList.remove('log');
// });