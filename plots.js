let Genre_data = {
    "Documentaries - Director: Vlad Yudin": 359,
    "Dramas & International Movies - Director: Youssef Chahine": 362,
    "Stand-Up Comedy - Director: Raúl Campos, Jan Suter": 334,
};

// Create an array of category labels
let labels = Object.keys(Genre_data);

// Create an array of values (the numerical data for the pie chart)
let values = Object.values(Genre_data);

// Display the default plot
function init() {
    // Default trace for the country data
    let trace = {
        values: values,  // Use the array of numerical values
        labels: labels,  // Use the array of labels
        type: "pie",
        sort: false // Ensure sectors are not reordered
    }

    // Data Array
    let data = [trace];

    // Layout object
    let layout = {
        height: 600,
        width: 800
    };

    // Render the plot to the div tag with id "pie"
    Plotly.newPlot("pie", data, layout);
}

init();
