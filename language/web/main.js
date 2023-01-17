Vue.component('attempt', {
    data: function() {
	return {
	    attempt: '',
	    icon: 'img/circle.svg',
	}
    },
    props: ['word'],
    template: `\
<span>
    <img :src="icon" height="16" width="16">
    <input v-model.lazy="attempt" v-on:change="changed">
</span>`,
    methods: {
	changed: function() {
	    console.log(`Attempt="${this.attempt}"` +
			` ${this.attempt === this.word.he ? 'ok': 'NOK'}`)
	    this.icon = this.attempt === this.word.he ?
		'img/check-circle-fill.svg' :
		'img/x-circle-fill.svg'
	}
    }
})

const app = new Vue({
    el: '#app',
    data: {
	words: [],
	lesson: 1,
	options: [
	    {text: 'Lesson 1', value: 1},
	    {text: 'Lesson 2', value: 2},
	],
	fontName: 'Calibri',
	fonts: [
	    'Calibri',
	    'Narkisim',
	    'Cafe',
	],
    },
    created () {
	// FIXME La référence à {lesson} ne marche pas, pourquoi ? data pas encore dispo lors du created ?
	// fetch('https://raw.githubusercontent.com/joaomdsc/sample/main/language/lesson{lesson}.json')
	fetch('https://raw.githubusercontent.com/joaomdsc/sample/main/language/lesson1.json')
	    .then(r => r.json())
	    .then(x => {
		this.words = x.words
	    })
    },
    // FIXME computed or watch ?
    computed: {
	hebrewStyle: function() {
	    return {
		'fontFamily': this.fontName,
	    }
	},
    },
    watch: {
	lesson: function(val) {
	    fetch(`https://raw.githubusercontent.com/joaomdsc/sample/main/language/lesson${val}.json`)
		.then(r => r.json())
		.then(x => {
		    this.words = x.words
		})
	},
    },
})
