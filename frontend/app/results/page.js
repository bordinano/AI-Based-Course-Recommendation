"use client";

import { useContext, useState, useEffect } from "react";
import { StudentContext } from "@/context/StudentContext";
import { useRouter } from "next/navigation";
import { getResults } from "@/services/api";
import ThinkerLogo from "@/components/ThinkerLogo";

export default function ResultsPage() {
  const { student, attemptId, clearData } = useContext(StudentContext);
  const router = useRouter();

  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [schoolFilter, setSchoolFilter] = useState("All"); // All, Public, Private

  // Fetch results on mount
  useEffect(() => {
    if (!student.studentId || !attemptId) {
      router.push("/student");
      return;
    }

    const fetchResults = async () => {
      setIsLoading(true);
      try {
        const data = await getResults(attemptId, schoolFilter === "All" ? null : schoolFilter);
        setResults(data);
      } catch (error) {
        setErrorMessage(error.message || "Failed to load results. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [student.studentId, attemptId, schoolFilter, router]);

  // Filter schools by type
  const filteredSchools = results?.recommended_schools?.filter((school) => {
    if (schoolFilter === "All") return true;
    return school.institution_type === schoolFilter;
  }) || [];

  const handleRetake = () => {
    clearData();
    router.push("/student");
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-linear-to-r from-[#cdffd8] to-[#94b9ff] flex items-center justify-center py-16">
        <div className="text-center">
          <ThinkerLogo />
          <p className="mt-4 text-lg text-gray-600">Generating your recommendations...</p>
        </div>
      </main>
    );
  }

  if (errorMessage) {
    return (
      <main className="min-h-screen bg-linear-to-r from-[#cdffd8] to-[#94b9ff] flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-md bg-white rounded-2xl p-8 shadow-sm text-center">
          <ThinkerLogo className="mx-auto" />
          <p className="mt-4 text-red-600">{errorMessage}</p>
          <div className="mt-6 flex gap-3 justify-center">
            <button
              onClick={() => router.push("/student")}
              className="rounded-full bg-white border border-gray-400 text-[#50505A] px-9 py-3 text-sm font-bold transition hover:bg-gray-50"
            >
              START OVER
            </button>
            <button
              onClick={handleRetake}
              className="rounded-full bg-[#50505A] px-9 py-3 text-sm font-bold text-white transition hover:bg-[#3f3f47]"
            >
              RETAKE ASSESSMENT
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (!results) {
    return null;
  }

  const topProgram = results.recommended_programs?.[0];
  const otherPrograms = results.recommended_programs?.slice(1) || [];

  return (
    <main className="min-h-screen bg-linear-to-r from-[#cdffd8] to-[#94b9ff] py-16 px-6">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-[#111827]">Assessment Completed</h1>
            <p className="text-gray-600 mt-1">
              Based on your assessment, our AI generated personalized recommendations.
            </p>
          </div>
          <ThinkerLogo />
        </div>

        {/* Best Recommendation */}
        {topProgram && (
          <div className="mb-10 bg-gradient-to-r from-[#283d7a] to-[#50505A] rounded-2xl p-8 text-white shadow-lg">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div>
                <p className="text-sm opacity-80 uppercase tracking-wide">Your Best Match</p>
                <h2 className="text-3xl md:text-4xl font-bold mt-1">{topProgram.program_name}</h2>
                <p className="mt-2 opacity-90">{topProgram.description}</p>
                <p className="mt-4 text-sm opacity-80">
                  {topProgram.explanation}
                </p>
              </div>
              <div className="flex flex-col items-center md:items-end gap-2">
                <p className="text-sm opacity-80">Compatibility Score</p>
                <div className="text-6xl md:text-7xl font-extrabold">
                  {topProgram.compatibility_score}%
                </div>
                <div className="flex gap-4 text-xs opacity-80 mt-2">
                  <span>Aptitude: {topProgram.components.aptitude}%</span>
                  <span>Interest: {topProgram.components.interest}%</span>
                  <span>Career: {topProgram.components.career}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Other Recommended Programs */}
        {otherPrograms.length > 0 && (
          <div className="mb-10">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-[#111827]">Other Recommended Programs</h2>
              <p className="text-sm text-gray-500">Sorted by compatibility score</p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {otherPrograms.map((program) => (
                <div
                  key={program.academic_program_id}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition"
                >
                  <h3 className="font-bold text-xl text-[#111827]">{program.program_name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{program.degree_level}</p>

                  <div className="mt-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Compatibility</span>
                      <span className="font-bold text-[#283d7a]">{program.compatibility_score}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-[#00a8e8] transition-all duration-500"
                        style={{ width: `${program.compatibility_score}%` }}
                      />
                    </div>
                  </div>

                  <details className="mt-4">
                    <summary className="text-sm text-gray-600 cursor-pointer hover:text-[#283d7a]">
                      Show score breakdown
                    </summary>
                    <div className="mt-2 space-y-1 text-sm text-gray-700">
                      <div className="flex justify-between">
                        <span>Aptitude</span>
                        <span className="font-medium">{program.components.aptitude}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Interest</span>
                        <span className="font-medium">{program.components.interest}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Career</span>
                        <span className="font-medium">{program.components.career}%</span>
                      </div>
                    </div>
                    <p className="mt-2 text-xs text-gray-500 italic">{program.explanation}</p>
                  </details>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommended Schools with Filter */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-[#111827]">
              Recommended Schools in Muntinlupa City
            </h2>

            {/* School Type Filter */}
            <div className="flex gap-2 bg-white rounded-full p-1 shadow-sm">
              {["All", "Public", "Private"].map((type) => (
                <button
                  key={type}
                  onClick={() => setSchoolFilter(type)}
                  className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
                    schoolFilter === type
                      ? "bg-[#283d7a] text-white"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <p className="text-gray-600 mb-6">
            Showing {filteredSchools.length} school{filteredSchools.length !== 1 ? "s" : ""} offering your recommended
            program{filteredSchools.length !== 1 ? "s" : ""}.
          </p>

          {filteredSchools.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <p className="text-gray-500">No schools match the selected filter.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredSchools.map((school) => (
                <div
                  key={`${school.school_id}-${school.program_id}`}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex flex-col md:flex-row md:items-center md:justify-between gap-4"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-bold text-[#111827]">{school.school_name}</h3>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          school.institution_type === "Public"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-purple-100 text-purple-700"
                        }`}
                      >
                        {school.institution_type}
                      </span>
                    </div>
                    <p className="mt-1 text-gray-600">
                      📚 <strong>{school.program_offered}</strong>
                    </p>
                    <p className="mt-1 text-gray-500 text-sm">📍 {school.address}</p>
                    {school.website_url && (
                      <a
                        href={school.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-2 inline-block text-sm text-[#283d7a] hover:underline"
                      >
                        Visit website →
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Disclaimer */}
        <div className="bg-yellow-50 border-l-4 border-yellow-500 p-5 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> The recommended schools are limited to educational institutions within Muntinlupa
            City that offer the recommended program. Students are encouraged to verify admission requirements and
            program availability directly with the institution.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={handleRetake}
            className="rounded-full bg-white border border-gray-400 text-[#50505A] px-9 py-3 text-sm font-bold transition hover:bg-gray-50"
          >
            RETAKE ASSESSMENT
          </button>
          <button
            onClick={() => router.push("/")}
            className="rounded-full bg-[#50505A] px-9 py-3 text-sm font-bold text-white transition hover:bg-[#3f3f47]"
          >
            BACK TO HOME
          </button>
        </div>
      </div>
    </main>
  );
}