/*
   _____ _____  _____        _____
  / ____|  __ \|  __ \      / ____|
 | |  __| |  | | |__) |   _| (___
 | | |_ | |  | |  ___/ | | |\___ \
 | |__| | |__| | |   | |_| |____) |
  \_____|_____/|_|    \__, |_____/
                       __/ |
                      |___/
The main JavaScript code for the GDPyS frontend portion.
*/

function IziSuccess(MainText, OtherText) {
    iziToast.success({
        id: 'success',
        title: MainText,
        message: OtherText,
        position: 'bottomRight',
        transitionIn: 'bounceInLeft'
        //onOpened:
        //onClosed: 
    });
}

function IziFail(MainText, OtherText) {
    iziToast.error({
        id: 'error',
        title: MainText,
        message: OtherText,
        position: 'bottomRight',
        transitionIn: 'bounceInLeft'
    });
}

function ReuploadLevel(LevelID) {
    fetch(`/tools/reuploadapi/${LevelID}`)
	.then(res => res.json())
	.then((out) => {
        if (out["status"] == 404) {
            IziFail("Error!", "Could not find origin level.")
        }
        else if (out["status"] == 500) {
            IziFail("Error!", "Something behind the scenes went terribly wrong.")
        }
        else {
            IziSuccess("Level Reuploaded!", `The level ID is ${out["levelID"]}!`)
        }
    })
    .catch(err => { IziFail("Error!", "Misc reupload error!") }); 
}
