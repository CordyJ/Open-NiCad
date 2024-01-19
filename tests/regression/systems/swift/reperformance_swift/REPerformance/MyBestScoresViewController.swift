//
//  MyBestScoresViewController.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-12.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit


class MyBestScoresViewController: UIViewController {
	
	// MARK: Outlets
	
	@IBOutlet fileprivate var myBestScoresTableView: UITableView?
	
	
	// MARK: - Properties
	
	var exerciseScores: ReportCardExerciseScores? {
		didSet {
			if let exerciseScores = self.exerciseScores {
				self.exerciseScoresViewModel = exerciseScores.generateExerciseScoresViewModel()
			}
			else {
				self.exerciseScoresViewModel = nil
			}
		}
	}
	
	fileprivate var exerciseScoresViewModel: [(ExerciseInfo, [ExerciseScoreAthleteCellViewModel])]? {
		didSet {
			if let exerciseScoresViewModel = self.exerciseScoresViewModel {
				var flattenedViewModel = [Any]()
				for exerciseScoresViewModelTuple in exerciseScoresViewModel {
					flattenedViewModel.append(exerciseScoresViewModelTuple.0)
					for exerciseScoreAthleteCellViewModel in exerciseScoresViewModelTuple.1 {
						flattenedViewModel.append(exerciseScoreAthleteCellViewModel)
					}
				}
				self.exerciseScoresViewModelCompact = flattenedViewModel
			}
			else {
				self.exerciseScoresViewModelCompact = nil
			}
		}
	}
	
	fileprivate var exerciseScoresViewModelCompact: [Any]? {
		didSet {
			self.myBestScoresTableView?.reloadData()
		}
	}
}


extension MyBestScoresViewController: UITableViewDataSource {
	
	func numberOfSections(in tableView: UITableView) -> Int {
		return 1
	}
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		guard let exerciseScoresViewModelCompact = self.exerciseScoresViewModelCompact else {
			return 0
		}
		
		return (exerciseScoresViewModelCompact.count + 1)
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		if indexPath.row == 0 {
			let cell = tableView.dequeueReusableCell(withIdentifier: "Best Scores Cell Identifier", for: indexPath)
			
			return cell
		}
		else if let exerciseInfo = self.exerciseScoresViewModelCompact![(indexPath.row - 1)] as? ExerciseInfo {
			let cell = tableView.dequeueReusableCell(withIdentifier: "Score Section Header", for: indexPath) as! MyScoreSectionHeaderTableViewCell
			cell.configure(with: exerciseInfo)
			
			return cell
		}
		else if let exerciseScoreAthleteCellViewModel = self.exerciseScoresViewModelCompact![(indexPath.row - 1)] as? ExerciseScoreAthleteCellViewModel {
			let cell = tableView.dequeueReusableCell(withIdentifier: "Score Cell Identifier", for: indexPath) as! ExerciseScoreAthleteTableViewCell
			cell.configure(with: exerciseScoreAthleteCellViewModel)
			
			return cell
		}
		
		fatalError()
	}
}
