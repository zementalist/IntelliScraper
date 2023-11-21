<template>
  <div class="container">
    <div class="row justify-content-center mt-3">
      <div class="col-12 text-center">
        <h2 class="display-2">Explore Companies</h2>

        <!-- <u-animate-container>
          <u-animate
      name="fadeIn"
      delay="0s"
      duration="1s"
      :iteration="1"
      :offset="0"
      animateClass="animated"
      :begin="true" 
    >        <h2 class="display-2">Explore Companies</h2>
</u-animate>
        </u-animate-container> -->
      </div>
    </div>
    <br />
    <br />
    <div class="row justify-content-around text-center">
      <div class="col-12 col-sm-8 pt-3 pb-3 border border-2 rounded we-border">
        <h3>
          <font-awesome-icon :icon="['fas', 'globe']" /> Select Country or
          Region
        </h3>
        <br />
        <p
          :class="
            selectedCountries.length == 0 ? 'mt-4 ml-2 invisible' : 'mt-4 ml-2'
          "
        >
          <b>Selection:</b>
          <span
            class="badge bg-secondary m-1"
            v-for="selection in selectedCountries"
            >{{ selection }}
          </span>
        </p>
        <DropdownCheckbox
          class="text-center"
          :title="'Country'"
          :items="data.countries"
          @selectionChange="updateSelCountry"
        >
        </DropdownCheckbox>
      </div>
    </div>
    <br />
    <div class="row justify-content-around text-center">
      <div class="col-12 col-sm-8 pt-3 pb-3 border border-2 rounded we-border">
        <h3>
          <font-awesome-icon :icon="['fas', 'industry']" /> Select Industry
        </h3>
        <br />
        <p
          :class="
            selectedIndustries.length == 0 ? 'mt-4 ml-2 invisible' : 'mt-4 ml-2'
          "
        >
          <b>Selection:</b>
          <span
            class="badge bg-secondary m-1"
            v-for="selection in selectedIndustries"
            >{{ selection }}
          </span>
        </p>
        <DropdownCheckbox
          class="text-center"
          :title="'Industry'"
          :items="data.industries"
          @selectionChange="updateSelIndustry"
        >
        </DropdownCheckbox>
      </div>
    </div>
    <br />
    <div class="row">
      <div class="col-12 text-center">
        <button @click="exploreCompanies" class="btn btn-lg btn-primary we-btn">
          Explore
        </button>
      </div>
    </div>
    <Spinner :size="4" :showSpinner="showExploreSpinner"></Spinner>
    <br /><br /><br />
    <ExploreTable
      :title="'Available Companies'"
      :dataset="dataset"
      :allowSelection="true"
      @update-selected-rows="updateSelCompany"
      v-if="dataset.length > 0"
    ></ExploreTable>

    <div class="row mt-3 pt-5 pb-3"  v-if="dataset.length > 0">
      <div class="col-12">
        <h2 class="display-2 text-center">Scraping Criteria</h2>
        <div class="row justify-content-around pt-5 pb-5">
          <div
            style="max-width: 33vw;"
            class="col-lg-4 col-md-6 col-12 m-3 mt-4"
            v-for="(criteria, index) in socialCriteriaList"
          >
            <SocialCriteria
              :index="index"
              :enabled="criteria.enabled"
              :label="criteria.label"
              :maxItems="criteria.maxItems"
              :title="criteria.title"
              :minDate="criteria.minDate"
              :itemCount="criteria.itemCount"
              :icon="criteria.icon"
              :selectedDate="criteria.selectedDate"
              @update-user-input="updateUserInputCriteria"
            ></SocialCriteria>
          </div>
        </div>
      </div>

      <div class="row mt-3 pt-3 pb-3 justify-content-around">
        <div class="col-4 text-center">
          <font-awesome-icon :icon="['fas', 'spider-black-widow']" />
          <button
            @click="scrapeAndAnalyze"
            class="btn btn-lg btn-primary we-btn"
          >
            Scrape & Analyze
          </button>
        </div>
        <div class="col-4 text-center">
          <button
            @click="createJob"
            class="btn btn-lg btn-primary we-btn"
          >
            Create Job
          </button>
          <select v-model="selectedFrequency" class="form-select form-select mt-3" aria-label=".form-select-lg example">
            <option value="" selected>Select Schedule*</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
          <select v-model="selectedOutputDriver" class="form-select form-select mt-3" aria-label=".form-select-lg example">
            <option value="" selected>Select Output Driver*</option>
            <option value="filesystem">Filesystem</option>
            <option value="database">Database</option>
          </select>
        </div>
      </div>
      <br /><br />
      <Spinner :size="4" :showSpinner="showAnalysisSpinner"></Spinner>

      <div class="row mt-3 pt-3 pb-3" v-if="showOffers">
        <h3 class="text-center card-title mt-5 mb-3 pb-4">
          Social Media & Offers Analysis
        </h3>

        <div class="col-12">
          <div id="accordion">
            <div class="card mt-5" v-for="(value, key, index) in analysisResults" :set="shortKey = key.replaceAll(' ','')">
              <div class="card-header text-center" :id="shortKey">
                  <button
                    class="btn btn-link social-title"
                    data-bs-toggle="collapse"
                    :data-bs-target="'#collapse-'+shortKey+'-id'"
                    aria-expanded="true"
                    :aria-controls="shortKey+'-id'"
                  >
                    <h3 class="mb-0 display-6">{{ key }}</h3>
                  </button>
              </div>

              <div
                :id="`collapse-${shortKey}-id`"
                class="collapse"
                :aria-labelledby="`heading-${shortKey}-id`"
                data-bs-parent="#accordion"
              >
                <div class="card-body ml-2">
                  <div :id="`accordion-${shortKey}-twitter-id`">
                    <div class="card">
                      <div class="card-header" :id="`heading-${shortKey}-id-2`">
                          <button
                            class="btn btn-link social-title"
                            data-bs-toggle="collapse"
                            :data-bs-target="`#collapse-${shortKey}-id-2`"
                            aria-expanded="true"
                            :aria-controls="`#collapse-${shortKey}-id-2`"
                          >
                          <h3 class="mb-0 display-6">Twitter</h3>
                          </button>
                      </div>

                      <div
                        :id="`collapse-${shortKey}-id-2`"
                        class="collapse"
                        :aria-labelledby="`heading-${shortKey}-id`"
                        :data-bs-parent="`accordion-${shortKey}-twitter-id`"
                      >
                        <div class="card-body"
                        v-if="analysisResults[key]['twitter'] ?? false"
                        >
                          <ExploreTable
                            
                            :title="'Twitter'"
                            :allowSelection="false"
                            :dataset="analysisResults[key]['twitter']"
                          ></ExploreTable>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="card-body ml-2">
                  <div :id="`accordion-${shortKey}-youtube-id`">
                    <div class="card">
                      <div class="card-header" :id="`heading-${shortKey}-id-3`">
                          <button
                            class="btn btn-link social-title"
                            data-bs-toggle="collapse"
                            :data-bs-target="`#collapse-${shortKey}-id-3`"
                            aria-expanded="true"
                            :aria-controls="`collapse-${shortKey}-id-3`"
                          >
                            <h3 class="mb-0 display-6 social-title">YouTube</h3>
                          </button>
                      </div>

                      <div
                        :id="`collapse-${shortKey}-id-3`"
                        class="collapse"
                        :aria-labelledby="`heading-${shortKey}-id-3`"
                        :data-bs-parent="`#accordion-${shortKey}-id-3`"
                      >
                        <div class="card-body"
                        v-if="analysisResults[key]['youtube'] ?? false"
                        >
                          <ExploreTable
                            
                            :title="'YouTube'"
                            :allowSelection="false"
                            :dataset="analysisResults[key]['youtube']"
                          ></ExploreTable>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, getCurrentInstance } from "vue";
import DropdownCheckbox from "../components/DropdownCheckbox.vue";
import SocialCriteria from "../components/SocialCriteria.vue";
import Spinner from "../components/Spinner.vue";
import ExploreTable from "../components/ExploreTable.vue";

const axios = getCurrentInstance().appContext.config.globalProperties.axios;
let data = reactive({ countries: [], industries: [] });
let dataset = ref([]);
let selectedCountries = ref([]);
let selectedIndustries = ref([]);

let selectedFrequency = ref("")
let selectedOutputDriver = ref("")

let showAnalysisSpinner = ref(false);
let showExploreSpinner = ref(false);

let showOffers = ref(false);

let selectedCompaniesIds = ref([]);

let socialCriteriaList = [
  {
    enabled: true,
    itemCount: 25,
    selectedDate: "",
    title: "Twitter",
    label: "Tweets",
    maxItems: 100,
    minDate: new Date(new Date().setMonth(new Date().getMonth() - 3))
      .toISOString()
      .split("T")[0],
    icon: {
      class: ["fab", "twitter"],
      color: "#1DA1F2",
    },
  },
  {
    enabled: true,
    selectedDate: "",
    title: "YouTube",
    label: "Videos",
    maxItems: 50,
    minDate: new Date(new Date().setMonth(new Date().getMonth() - 3))
      .toISOString()
      .split("T")[0],
    itemCount: 10,
    icon: {
      class: ["fab", "youtube"],
      color: "#c4302b",
    },
  },
  // {
  //   enabled: true,
  //   title: "Maps",
  //   label: "Locations",
  //   itemCount: -1,
  //   icon: {
  //     class: ["fas", "map-location-dot"],
  //     color: "#227020",
  //   },
  // },
];
function updateSelCountry(countries) {
  selectedCountries.value = countries;
}
function updateSelIndustry(industries) {
  selectedIndustries.value = industries;
}
function updateSelCompany(comapniesIds) {
  selectedCompaniesIds.value = comapniesIds;
}
function updateUserInputCriteria(criteria) {
  for (let key in criteria)
    socialCriteriaList[criteria.index][key] = criteria[key];
}

onMounted(() => {
  let path = process.env.NODE_ENV === 'production' ? '/assets/region-countries.json' : '/src/assets/region-countries.json';
  path = "/get_countries"
  axios.get(path).then(response => {
    if (response.status == 200) {
      let countries = response.data.result
      data.countries = ["All Countries"].concat(countries);
    }
  })
  path = "/get_industries"
  axios.get(path).then(response => {
    if (response.status == 200) {
      data.industries = response.data.result;
    }
  })
});


let exploreCompanies = () => {
  let url = "/get_companies?";
  if (selectedCountries.value.length > 0 || selectedIndustries.value.length > 0) {
    selectedCountries.value.forEach((country) => {
      url += `countries_list=${country}&`;
    });
    selectedIndustries.value.forEach((industry) => {
      url += `industries_list=${industry}&`;
    });
    console.log(url);
    showExploreSpinner.value = true;
    axios.get(url).then((jsonRes) => {
      console.log(jsonRes);

      let companies = jsonRes.data.result ?? [];
      console.log(companies);

      // Reset value & async reassign to give the effect
      // of reactivity
      // (since the condition above(length > 0)) gives same result
      // after the first update
      dataset.value = [];
      setTimeout(() => {
        dataset.value = companies;
        showExploreSpinner.value = false;
      }, 1);
    });
  }
};

let youtubeResult = ref([
  {
    content: "This is the first offer 50%",
    satisfaction_rate: 87,
    views: 100000,
    comments_count: 100,
    likes_count: 714,
    img: "https://blog.logrocket.com/wp-content/uploads/2019/09/Vue-event-bus-nocdn.png",
    url: "https://www.youtube.com",
  },
  {
    content: "This is the second offer 80%",
    satisfaction_rate: 61,
    views: 23000,
    comments_count: 500,
    likes_count: 20,
    img: "https://blog.logrocket.com/wp-content/uploads/2019/09/Vue-event-bus-nocdn.png",
    url: "https://www.youtube.com",
  },
]);
let analysisResults = ref({
  "Telecom Egypt": {"twitter": youtubeResult, "youtube":youtubeResult},
  "Vodafone": {"twitter": null, "youtube":null},
});

let scrapeAndAnalyze = () => {
  showAnalysisSpinner.value = true;
  const url = "/scrape_social";
  let body = {
    criteria: {},
    company_ids: selectedCompaniesIds.value,
  };
  for (let criteria of socialCriteriaList) {
    body.criteria[criteria.title.toLowerCase()] = {
      enabled: criteria.enabled,
      itemCount: criteria.itemCount,
      publishDateEnd: criteria.selectedDate,
    };
  }
  // setTimeout(()=>{showOffers.value=true;showAnalysisSpinner.value=false;},2000)
  axios.post(url, (data = body)).then((jsonRes) => {
    console.log(jsonRes);
    
    showAnalysisSpinner.value = false;
    // youtubeResult.value = [];
    analysisResults.value = {}
    setTimeout(() => {
      // console.log(jsonRes.data.results["Telecom Egypt"].youtube);
      analysisResults.value = jsonRes.data.result;
      console.log(analysisResults)
      showOffers.value = true;
    }, 1);
    // let results = jsonRes.body.results ?? []
    // console.log(results);
    // TODO: Show {
    //   [Twitter(offer, satisfactionRate, interaction, date)],
    //   [YouTube(......, satisfactionRate, interactions, viewCount, date)],
    // }
  });
};

let createJob = () => {
  const url = "/insert_jobs";
  let jobs = [];

  for (let criteria of socialCriteriaList) {
    if (criteria.enabled) {
        let job = {
          social_platform_name: criteria.title.toLocaleLowerCase(),
          items_count: criteria.itemCount,
          publish_date_limit: criteria.selectedDate,
          frequency: selectedFrequency.value,
          output_format_type: selectedOutputDriver.value
        }
        jobs.push(job)
    }
  }
  let body = {
    jobs: jobs,
    companies_ids: selectedCompaniesIds.value,
  };
  console.log(selectedCompaniesIds)
  // setTimeout(()=>{showOffers.value=true;showAnalysisSpinner.value=false;},2000)
  axios.post(url, body).then((jsonRes) => {
    console.log(jsonRes);
    alert("Jobs are added successfully")

  });
};
</script>

<style scoped>
.ml-2 {
  margin-left: 2rem;
}
.social-title {
  text-decoration-line: none;

}
</style>
