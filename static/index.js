function deletefile(id){
    fetch('/delete-file', {
        method: "POST",
        body: JSON.stringify({file_id: id})
    }).then((_res) => {
        window.location.href = '/manage'
    })
}


function locate(loc){
    window.location.href = '/'+loc
}

function resendotp(link){
    fetch('/resend-otp', {
        method: "POST",
        body: JSON.stringify({link: link})
    }).then((_res) => {
        locate('verify/'+link)
    })
}