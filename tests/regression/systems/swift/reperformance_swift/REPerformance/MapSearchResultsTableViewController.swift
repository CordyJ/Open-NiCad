//
//  MapSearchResultsTableViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import GoogleMaps
import GooglePlaces

class MapSearchResultsTableViewController: UITableViewController {
    
    var mapSearchDelegate:MapSearchDelegate? = nil
    var mapView:GMSMapView? = nil
    var googleDataProvider = GoogleDataProvider()
    
    let placesClient = GMSPlacesClient()
    
    var matchingItems:[REPPlace] = []

    // MARK: - Table view data source

    override func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return matchingItems.count
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: Constants.GymLeaderboard.MapSearchResultsCellID, for: indexPath)

        cell.textLabel?.text = matchingItems[indexPath.row].name
        cell.detailTextLabel?.text = matchingItems[indexPath.row].vicinity

        return cell
    }
    
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let selectedItem = matchingItems[indexPath.row]
        dismiss(animated: true) { 
            self.mapSearchDelegate?.didSelectLocation(repPlace: selectedItem)
        }
    }

}

extension MapSearchResultsTableViewController:UISearchBarDelegate {
    func searchBar(_ searchBar: UISearchBar, textDidChange searchText: String) {
        NSObject.cancelPreviousPerformRequests(withTarget: self)
        self.perform(#selector(getSearchResults(searchText:)), with: searchText, afterDelay: 0.2)
    }
    
    @objc func getSearchResults(searchText:String){
        if let location = mapView?.myLocation?.coordinate {
            googleDataProvider.searchNearbyPlaces(location: location, queryString: searchText, completion: { (REPPlaces, pageToken, error) in
                if let error = error {
                    print("Error searching: \(error)")
                    self.matchingItems = []
                    self.tableView.reloadData()
                } else {
                    if let repPlaces = REPPlaces {
                        self.matchingItems = repPlaces
                    } else {
                        self.matchingItems = []
                    }
                    self.tableView.reloadData()
                }
            })
        }
    }
}
