Vue.component('attempt', {
    data: function() {
	return {
	    attempt: '',
	}
    },
    props: ['word'],
    template: '<input v-model.lazy="attempt" v-on:change="changed">',
    methods: {
	changed: function() {
	    console.log(`Attempt="${this.attempt}"` +
			` ${this.attempt === this.word.he ? 'ok': 'NOK'}`)
	}

    }
})

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
