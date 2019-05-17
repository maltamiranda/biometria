

function setup(){
	foo = new p5.SpeechRec('es-AR'); // speech recognition object (will prompt for mic access)
	foo.onResult = showResult; // bind callback function to trigger when speech is recognized
	foo.start(); // start listening
}


function showResult()
{
  //console.log(foo.resultString); // log the result
  alert(foo.resultString);

}


function touchStarted() {
	getAudioContext().resume()
}
