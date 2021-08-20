$(document).ready(function () {
  $('input[type=radio][id=output-type-pie]').click()
})

$('input[type=radio][name=output-type]').change(function () {
    const outputId = this.id.replace('output-type-', '#output-')
    showOutput(outputId)
  },
)

function showOutput (outputId) {
  $('#output-line').hide()
  $('#output-table').hide()
  $('#output-pie').hide()

  $(outputId).show()
}
