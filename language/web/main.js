const app = new Vue({
    el: '#app',
    data: {
	words: [],
    },
    created () {
	fetch('https://raw.githubusercontent.com/joaomdsc/sample/main/language/lesson2.json')
	    .then(r => r.json())
	    .then(x => {
		this.words = x.words
	    })
    },
})
