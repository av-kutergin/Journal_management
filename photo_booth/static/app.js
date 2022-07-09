new Vue({
    el: '#photos_app',
    data: {
    photos: []
    },
    created: function () {
        const vm = this;
        axios.get('/api/photos/')
        .then(function (response){
        vm.photos = response.data
        })
    }
}
)
