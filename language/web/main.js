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
    },
    created () {
	fetch('https://raw.githubusercontent.com/joaomdsc/sample/main/language/lesson2.json')
	    .then(r => r.json())
	    .then(x => {
		this.words = x.words
	    })
    },
})
