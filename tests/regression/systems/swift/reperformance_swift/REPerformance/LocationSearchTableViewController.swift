//
//  LocationSearchTableViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-17.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

enum LocationDisplay:Int{
    case Country
    case Province
}

struct LocationsSearchViewData{
    let locationDisplay:LocationDisplay
    let locations:Locations
    let countryID:String?
    let provinceID:String?
}

class LocationSearchTableViewController: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    @IBOutlet private var tableView:UITableView?
    
    var viewData:LocationsSearchViewData?
    var filteredCountries:Array<Country> = []
    var filteredProvinces:Array<Province> = []
    let searchController:UISearchController = UISearchController(searchResultsController: nil)
    
    var dismiss: (()->())?
    var selectedCountry: ((_ countryID:String)->())?
    var selectedProvince: ((_ provinceID:String)->())?

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationItem.rightBarButtonItem = UIBarButtonItem(barButtonSystemItem: .done, target: self, action: #selector(doneTapped))
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        guard let viewData = self.viewData else {
            doneTapped()
            return
        }
        switch viewData.locationDisplay {
        case .Country:
            self.title = "Select a Country"
        case .Province:
            self.title = "Select a Province"
        }
        setUpSearchController()
    }
    
    func setUpSearchController(){
        searchController.searchResultsUpdater = self
        searchController.dimsBackgroundDuringPresentation = false
        definesPresentationContext = true
        tableView?.tableHeaderView = searchController.searchBar
        searchController.searchBar.barTintColor = UIColor(named: .rePerformanceBlue)
        searchController.searchBar.tintColor = UIColor(named: .rePerformanceOrange)
        
        //This is weird behaviour with the search bar. In order to get a see through background to see the background image this needs to be done. Doesn't seem to work in storyboard.
        self.tableView?.backgroundView = UIView()
        self.tableView?.backgroundView?.backgroundColor = UIColor.clear
        self.tableView?.backgroundColor = UIColor.clear
    }
    
    @objc func doneTapped(){
        dismiss?()
    }

    // MARK: - Table view data source

    func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        guard let viewData = self.viewData else {
            return 0
        }
        switch viewData.locationDisplay {
        case .Country:
            if searchController.isActive && searchController.searchBar.text != "" {
                return filteredCountries.count
            }
            return viewData.locations.countries.count
        case .Province:
            if searchController.isActive && searchController.searchBar.text != "" {
                return self.filteredProvinces.count
            }
            for country in viewData.locations.countries{
                if country.id == viewData.countryID
                {
                    return country.provinces.count
                }
            }
        }
        return 0
    }

    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let locationCell = tableView.dequeueReusableCell(withIdentifier: Constants.Profile.LocationCellIdentifier, for: indexPath)
        locationCell.textLabel?.textColor = UIColor(named: .rePerformanceOrange)
        guard let viewData = self.viewData else {
            locationCell.textLabel?.text = "Error"
            return locationCell
        }
        var text:String = ""
        var checkmark:Bool = false
        switch viewData.locationDisplay{
        case .Country:
            if searchController.isActive && searchController.searchBar.text != "" {
                text = filteredCountries[indexPath.row].name
                if filteredCountries[indexPath.row].name == viewData.countryID {
                    checkmark = true
                }
            } else {
                text = viewData.locations.countries[indexPath.row].name
                if viewData.locations.countries[indexPath.row].id == viewData.countryID {
                    checkmark = true
                }
            }
        case .Province:
            if searchController.isActive && searchController.searchBar.text != "" {
                text = filteredProvinces[indexPath.row].name
                if filteredProvinces[indexPath.row].id == viewData.provinceID{
                    checkmark = true
                }
            } else {
                for country in viewData.locations.countries{
                    if country.id == viewData.countryID{
                        text = country.provinces[indexPath.row].name
                        if country.provinces[indexPath.row].id == viewData.provinceID {
                            checkmark = true
                        }
                    }
                }
            }
        }
        locationCell.textLabel?.text = text
        if checkmark {
            locationCell.accessoryType = .checkmark
        } else {
            locationCell.accessoryType = .none
        }
        return locationCell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        guard let viewData = self.viewData else {
            return
        }
        switch viewData.locationDisplay{
        case .Country:
            if searchController.isActive && searchController.searchBar.text != "" {
                selectedCountry?(filteredCountries[indexPath.row].id)
            } else {
                selectedCountry?(viewData.locations.countries[indexPath.row].id)
            }
        case .Province:
            if searchController.isActive && searchController.searchBar.text != "" {
                selectedProvince?(filteredProvinces[indexPath.row].id)
            } else {
                for country in viewData.locations.countries{
                    if country.id == viewData.countryID{
                        selectedProvince?(country.provinces[indexPath.row].id)
                    }
                }
            }
        }
        
        
    }
    
    func filterLocationsWithSearch(_ searchText:String){
        guard let viewData = self.viewData else {
            return
        }
        switch viewData.locationDisplay {
        case .Country:
            filteredCountries = viewData.locations.countries.filter({ (country : Country) -> Bool in
                return country.name.lowercased().contains(searchText.lowercased()) || country.id.lowercased().contains(searchText.lowercased())
            })
        case .Province:
            for country in viewData.locations.countries{
                if country.id == viewData.countryID{
                    filteredProvinces = country.provinces.filter({ (province:Province) -> Bool in
                        return province.name.lowercased().contains(searchText.lowercased()) || province.id.lowercased().contains(searchText.lowercased())
                    })
                }
            }
        }
        tableView?.reloadData()
    }
}

extension LocationSearchTableViewController:UISearchResultsUpdating{
    func updateSearchResults(for searchController: UISearchController) {
        guard let searchBarText = searchController.searchBar.text else {
            return
        }
        filterLocationsWithSearch(searchBarText)
    }
}
