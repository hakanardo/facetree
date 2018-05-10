database = {
    "individuals": {},
    "families": {},
    "parentin": {},
    "childin": {}
};

function add_to_index_set(index, individual_id, family) {
    if (!index[individual_id]) {
        index[individual_id] = new Set();
    }
    index[individual_id].add(family);
}

function database_add_records(records) {
    for (var i in records) {
        var rec = records[i];
        if (rec.type == 'Individual') {
            if (!database.individuals[rec.id] || database.individuals[rec.id].version < rec.version) {
                database.individuals[rec.id] = rec;
            }
        } else if (rec.type == 'Family') {
            old_rec = database.families[rec.id];
            if (!old_rec || database.families[rec.id].version < rec.version) {
                if (old_rec) {
                    database.parentin[old_rec.father].delete(old_rec.id);
                    database.parentin[old_rec.mother].delete(old_rec.id);
                    for (var c in old_rec.children) {
                        database.childin[old_rec.children[c]].delete(old_rec.id);
                    }
                }
                add_to_index_set(database.parentin, rec.father, rec.id);
                add_to_index_set(database.parentin, rec.mother, rec.id);
                for (var c in rec.children) {
                    add_to_index_set(database.childin, rec.children[c], rec.id);
                }
                database.families[rec.id] = rec;
            }
        } else {
            console.log("Unknown record type:", rec);
        }
    }
    if (records.length > 0 && database.updated_cb) {
        database.updated_cb(records);
    }
}

function database_poll(since) {
    setTimeout(function () {
        axios.get(facetree_backend + "/v1/updates/" + since, {"headers": auth_headers})
        .then(function (response) {
            auth_token = response.data.token;
            database_add_records(response.data.records);
            database_poll(response.data.since);
        })
        .catch(function (error) {
            console.log("Database longpoll failed.", error)
        });

    }, 1);
}

function database_download() {
    axios.get(facetree_backend + "/v1/records", {"headers": auth_headers})
    .then(function (response) {
        database_add_records(response.data);
    })
    .catch(function (error) {
        console.log("Records failed.", error)
    });
}

function start_database_updater(auth_token, updated_cb) {
    database.updated_cb = updated_cb;
    auth_headers = {"Authorization": "Bearer " + auth_token};
    database_poll("NOW");
    setTimeout(database_download, 10);
}
